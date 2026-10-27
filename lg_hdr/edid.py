"""Validate and patch byte copies; this module never reads or writes devices."""
from dataclasses import dataclass
import hashlib

HEADER = bytes.fromhex('00ffffffffffff00')
LG_ID = bytes.fromhex('1e6d6677')  # GSM, product 0x7766 (little endian)

class EdidError(ValueError):
    """Malformed, unsupported, or ambiguous EDID."""

@dataclass(frozen=True)
class HdrBlock:
    extension: int
    header_offset: int
    eotf: int
    descriptors: int

    @property
    def pq(self):
        return bool(self.eotf & 4)

    @property
    def type1(self):
        return bool(self.descriptors & 1)

    @property
    def descriptor_offset(self):
        return self.header_offset + 3


def validate(data: bytes) -> None:
    if len(data) < 128 or len(data) % 128:
        raise EdidError('EDID length must be a nonzero multiple of 128 bytes.')
    if data[:8] != HEADER:
        raise EdidError('Invalid EDID header.')
    if len(data) != (data[126] + 1) * 128:
        raise EdidError('Extension count does not match file length.')
    for start in range(0, len(data), 128):
        if sum(data[start:start+128]) % 256:
            raise EdidError(f'Invalid checksum in block {start // 128}.')


def hdr_blocks(data: bytes) -> list[HdrBlock]:
    validate(data)
    blocks = []
    for start in range(128, len(data), 128):
        if data[start] != 2:
            continue
        end = data[start+2]
        if end == 0:  # CTA block has no data block collection or DTDs
            continue
        if not 4 <= end <= 127:
            raise EdidError('Invalid CTA data-block boundary.')
        pos = start + 4
        while pos < start + end:
            header = data[pos]
            size = header & 31
            if pos + 1 + size > start + end:
                raise EdidError('CTA data block extends beyond its collection.')
            if header >> 5 == 7 and size > 0 and data[pos+1] == 6:
                if size < 3:
                    raise EdidError('Truncated HDR Static Metadata block.')
                blocks.append(HdrBlock(start // 128, pos, data[pos+2], data[pos+3]))
            pos += size + 1
    return blocks


def inspect(data: bytes) -> dict:
    blocks = hdr_blocks(data)
    return {
        'bytes': len(data),
        'sha256': hashlib.sha256(data).hexdigest(),
        'manufacturer_hex': data[8:10].hex(),
        'product_id': f'0x{int.from_bytes(data[10:12], "little"):04x}',
        'supported_model': data[8:12] == LG_ID,
        'checksums_valid': True,
        'hdr': [{'offset': f'0x{b.header_offset:x}', 'pq': b.pq,
                 'static_metadata_type1': b.type1} for b in blocks],
        'scope': 'Structural checks only; not complete EDID conformity or physical HDR validation.',
    }


def patch(data: bytes) -> tuple[bytes, list[dict]]:
    blocks = hdr_blocks(data)
    if data[8:12] != LG_ID:
        raise EdidError('Patch is restricted to LG GSM product 0x7766.')
    if len(blocks) != 1:
        raise EdidError('Expected exactly one unambiguous HDR Static Metadata block.')
    block = blocks[0]
    if not block.pq:
        raise EdidError('PQ capability is missing; this quirk is not applicable.')
    if block.type1:
        return data, []
    corrected = bytearray(data)
    corrected[block.descriptor_offset] |= 1
    start = block.extension * 128
    corrected[start+127] = (-sum(corrected[start:start+127])) & 255
    result = bytes(corrected)
    validate(result)
    changes = [{'offset': f'0x{i:x}', 'before': a, 'after': b}
               for i, (a, b) in enumerate(zip(data, result)) if a != b]
    if {int(c['offset'], 16) for c in changes} != {block.descriptor_offset, start+127}:
        raise EdidError('Unexpected change outside the metadata bit and CTA checksum.')
    return result, changes
