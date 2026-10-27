# EDIDs reais: LG GSM 0x7766

Os dois arquivos vieram do meu monitor LG UltraGear. Autorizei a publicação
do original e da cópia corrigida para que outras pessoas possam reproduzir a
análise offline.
Os dados podem conter número de série; não contêm configurações de rede do PC.
Os arquivos são evidências do caso investigado, não firmware universal para
outros monitores. O projeto não instala ou aplica nenhum deles.

| Arquivo | Origem | SHA-256 |
| --- | --- | --- |
| `lg-gsm7766-original.bin` | EDID lido do monitor, 384 bytes | `313f6ab5dcd9dfa9df565d58588a50a0f7bae4409c71523db32c199ff6e80223` |
| `lg-gsm7766-hdr-type1.bin` | Cópia corrigida, 384 bytes | `8755c1022186b71a36a14848c7dd00f3bfa1cdccffd73dc4bb9dea042bdd6769` |

As únicas diferenças são:

- Offset `0x9f`: `00` → `01`, anunciando Static Metadata Type 1.
- Offset `0xff`: `79` → `78`, recalculando o checksum CTA.

Os checksums de todos os blocos são válidos. Isso não equivale a conformidade
completa do EDID: o EDID de fábrica tem outras inconsistências que não são
alteradas por esta correção.
