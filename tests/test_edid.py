import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch as mock_patch
from lg_hdr.edid import EdidError, HEADER, LG_ID, hdr_blocks, inspect, patch
from lg_hdr.__main__ import doctor, main, regular_output


def checksum(data, start=0):
    data[start+127] = (-sum(data[start:start+127])) & 255


def fixture(descriptor=0, pq=True, payload=None):
    """Synthetic data only: no physical display EDID or serial number."""
    base = bytearray(128)
    base[:8] = HEADER
    base[8:12] = LG_ID
    base[18:20] = bytes([1, 4])
    base[126] = 1
    checksum(base)
    ext = bytearray(128)
    ext[:4] = bytes([2, 3, 0, 0])
    payload = bytes([0xe3, 6, 5 if pq else 1, descriptor]) if payload is None else payload
    ext[4:4+len(payload)] = payload
    ext[2] = 4+len(payload)
    checksum(ext)
    return bytes(base+ext)


class EdidTests(unittest.TestCase):
    def test_missing_type1_detected(self):
        report = inspect(fixture())
        self.assertTrue(report['supported_model'])
        self.assertTrue(report['hdr'][0]['pq'])
        self.assertFalse(report['hdr'][0]['static_metadata_type1'])

    def test_patch_changes_exactly_flag_and_checksum(self):
        original = fixture()
        corrected, changes = patch(original)
        self.assertEqual([int(x['offset'],16) for x in changes], [135,255])
        self.assertTrue(inspect(corrected)['checksums_valid'])
        self.assertTrue(inspect(corrected)['hdr'][0]['static_metadata_type1'])
        self.assertEqual(original[:128], corrected[:128])
        self.assertEqual(original[128:135], corrected[128:135])
        self.assertEqual(original[136:255], corrected[136:255])

    def test_existing_bits_preserved(self):
        corrected, _ = patch(fixture(descriptor=0x80))
        self.assertEqual(corrected[135], 0x81)

    def test_idempotent(self):
        corrected, _ = patch(fixture())
        self.assertEqual(patch(corrected), (corrected, []))

    def test_other_monitor_refused(self):
        data = bytearray(fixture()); data[10] ^= 1; checksum(data)
        with self.assertRaises(EdidError): patch(bytes(data))

    def test_pq_missing_refused(self):
        with self.assertRaises(EdidError): patch(fixture(pq=False))

    def test_empty_truncated_and_bad_header_refused(self):
        for data in (b'', b'x'*128, fixture()[:-1]):
            with self.subTest(size=len(data)), self.assertRaises(EdidError): inspect(data)

    def test_bad_checksum_refused(self):
        data = bytearray(fixture()); data[135] ^= 1
        with self.assertRaises(EdidError): patch(bytes(data))

    def test_extension_count_refused(self):
        data = bytearray(fixture()); data[126] = 0; checksum(data)
        with self.assertRaises(EdidError): patch(bytes(data))

    def test_invalid_cta_boundary_refused(self):
        data = bytearray(fixture()); data[130] = 3; checksum(data,128)
        with self.assertRaises(EdidError): inspect(bytes(data))

    def test_overrunning_data_block_refused(self):
        data = bytearray(fixture()); data[132] = 0xff; checksum(data,128)
        with self.assertRaises(EdidError): inspect(bytes(data))

    def test_truncated_hdr_refused(self):
        with self.assertRaises(EdidError): patch(fixture(payload=bytes([0xe1,6])))

    def test_duplicate_hdr_refused(self):
        with self.assertRaises(EdidError): patch(fixture(payload=bytes([0xe3,6,5,0])*2))

    def test_absent_hdr_refused(self):
        with self.assertRaises(EdidError): patch(fixture(payload=b''))

    def test_missing_cta_collection_ignored(self):
        data = bytearray(fixture()); data[130] = 0; checksum(data,128)
        self.assertEqual(hdr_blocks(bytes(data)), [])

    def test_other_extension_preserved(self):
        data = bytearray(fixture()); data[126] = 2; checksum(data)
        extra = bytearray(128); extra[0] = 0x70; checksum(extra)
        data += extra
        corrected, _ = patch(bytes(data))
        self.assertEqual(corrected[256:], bytes(extra))


class FileAndCliTests(unittest.TestCase):
    def test_existing_output_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'out.bin'; p.write_bytes(b'keep')
            with self.assertRaises(FileExistsError): regular_output(p,b'new')
            self.assertEqual(p.read_bytes(),b'keep')

    def test_output_symlink_not_followed(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp)/'keep'; p.write_bytes(b'keep')
            link = Path(temp)/'out'; link.symlink_to(p)
            with self.assertRaises(FileExistsError): regular_output(link,b'new')
            self.assertEqual(p.read_bytes(),b'keep')

    def test_system_destination_refused(self):
        with self.assertRaises(EdidError): regular_output(Path('/etc/lg-hdr-test.bin'),b'new')

    def test_sudo_refused(self):
        with mock_patch('lg_hdr.__main__.os.geteuid',return_value=0), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(['doctor']),2)

    def test_offline_cli_preserves_source(self):
        with tempfile.TemporaryDirectory() as temp:
            src=Path(temp)/'source.bin'; dest=Path(temp)/'copy.bin'; src.write_bytes(fixture())
            out=io.StringIO()
            with mock_patch('lg_hdr.__main__.os.geteuid',return_value=1000), contextlib.redirect_stdout(out):
                self.assertEqual(main(['patch',str(src),str(dest)]),0)
            self.assertEqual(src.read_bytes(),fixture())
            self.assertFalse(json.loads(out.getvalue())['installed'])
            self.assertTrue(inspect(dest.read_bytes())['hdr'][0]['static_metadata_type1'])

    def test_doctor_only_connected_and_no_raw_data(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for name,status in [('card1-DP-3','connected'),('card1-DP-2','disconnected')]:
                d=root/name; d.mkdir(); (d/'status').write_text(status); (d/'edid').write_bytes(fixture())
            report=doctor(root)
            self.assertTrue(report['read_only'])
            self.assertEqual(len(report['displays']),1)
            self.assertNotIn('serial', json.dumps(report).lower())
            self.assertNotIn('00ffffffffffff00',json.dumps(report))


if __name__ == '__main__': unittest.main()


class AuthorizedRealFixtureTests(unittest.TestCase):
    def test_real_edid_matches_authorized_correction_exactly(self):
        root=Path(__file__).resolve().parents[1]/'examples'/'edid'
        original=(root/'lg-gsm7766-original.bin').read_bytes()
        expected=(root/'lg-gsm7766-hdr-type1.bin').read_bytes()
        result,changes=patch(original)
        self.assertEqual(result,expected)
        self.assertEqual([c['offset'] for c in changes],['0x9f','0xff'])
        self.assertTrue(inspect(expected)['checksums_valid'])
