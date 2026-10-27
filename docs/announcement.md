# Texto para compartilhar / Sharing draft

Este texto descreve resultados observados no meu PC. Não apresenta a correção
como descoberta inédita nem como solução universal. A publicação deste arquivo
no repositório não significa que o texto foi postado em outras comunidades.

## Português

**Título:** Investiguei um congelamento de HDR no meu LG UltraGear no Linux: um bit ausente no EDID

Tentei usar HDR no meu LG UltraGear, identificado como GSM 0x7766, com Arch Linux,
Hyprland e uma RTX 4060 Ti. Ao ativar HDR, a imagem ficava apagada e depois o
monitor congelava.

Na investigação, o EDID anunciava PQ/ST2084, mas deixava desligado o bit Static
Metadata Type 1, que a NVIDIA 615.78.08 exige para considerar a saída compatível
com HDR. Encontrei também uma proposta de patch anterior para esse mesmo defeito;
não estou reivindicando a descoberta original.

Preparei uma correção offline que altera o bit em `0x9f` de `00` para `01` e
recalcula o checksum CTA em `0xff` de `79` para `78`. Os outros bytes ficam iguais.
Depois de aplicar o override manualmente, os logs mostraram 1440p a aproximadamente
165 Hz, formato de 10 bits e preset HDR, sem o congelamento completo anterior
naquele teste.

Publiquei as ferramentas, os EDIDs reais do meu monitor, as diferenças exatas e
29 testes automatizados. A ferramenta distribuída **só diagnostica e gera uma
cópia local**; não instala firmware nem altera drivers ou boot.

Ainda não validei calibração, instalação persistente ou funcionamento em outros
monitores. O vídeo HDR no Firefox/YouTube continua em investigação por causa de
uma aparência lavada.

Projeto: https://github.com/xHitech/lg-ultragear-hdr-linux

Evidências: https://github.com/xHitech/lg-ultragear-hdr-linux/blob/main/docs/investigation.md

Patch anterior: https://www.mail-archive.com/dri-devel%40lists.freedesktop.org/msg630093.html

Se você tem um monitor GSM 0x7766 com um problema parecido, relatos do EDID e da
combinação de GPU/driver/compositor podem ajudar a entender o alcance do defeito.
Não é necessário aplicar o override para compartilhar um diagnóstico.

## English

**Title:** Investigating an HDR freeze on my LG UltraGear under Linux: a missing EDID capability bit

I tried enabling HDR on my LG UltraGear, identified as GSM 0x7766, with Arch Linux,
Hyprland, and an RTX 4060 Ti. The image initially looked dim, and then the display
froze.

The EDID advertised PQ/ST2084 but did not advertise Static Metadata Type 1, a
capability NVIDIA 615.78.08 requires for HDR. I also found an earlier upstream
patch proposal for this exact quirk, so I am not claiming the original discovery.

I put together an offline correction that changes `0x9f` from `00` to `01` and
recalculates the CTA checksum at `0xff` from `79` to `78`, preserving every other
byte. After I manually applied the override, compositor logs showed 1440p at
approximately 165 Hz, a 10-bit format, and the HDR preset. I did not experience
the previous complete freeze in that trial.

The repository includes read-only diagnostics, offline correction, my authorized
real EDID fixtures, exact byte changes, and 29 automated tests. The distributed
tool **does not install or activate the override** or change drivers or boot.

Color calibration, persistent installation, and other display models are not
validated. Native HDR playback in Firefox/YouTube remains under investigation
because the video appeared washed out.

Project: https://github.com/xHitech/lg-ultragear-hdr-linux

Evidence: https://github.com/xHitech/lg-ultragear-hdr-linux/blob/main/docs/investigation.en.md

Earlier patch proposal: https://www.mail-archive.com/dri-devel%40lists.freedesktop.org/msg630093.html

If you have a GSM 0x7766 display with similar symptoms, EDID findings and your
GPU/driver/compositor combination would help establish which setups are affected.
Applying an override is not required to contribute a diagnostic report.
