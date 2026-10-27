# Evidências do caso investigado

Ambiente: Arch Linux, NVIDIA RTX 4060 Ti, nvidia-open/NVIDIA 615.78.08,
Hyprland 0.56.2, Aquamarine 0.15.1 e Firefox 158.0.1.

Este resumo contém apenas informações técnicas selecionadas. Não inclui
endereços de rede, credenciais, URLs assinadas, cookies ou dumps de memória.

## Antes da correção do EDID

As sondagens de validação atômica do driver retornaram:

| Variante | Resultado |
| --- | --- |
| HDR original | EINVAL (22) |
| Sem BT2020 | EINVAL (22) |
| Sem metadados HDR | EINVAL (22) |
| Sem BT2020 e sem metadados HDR | Aceita |
| Sem cursor de hardware | EINVAL (22) |
| Sem fence de entrada | EINVAL (22) |

As associações de CRTC no kernel e no backend coincidiam nessa rodada;
portanto, uma divergência de associação não explicou o caso.

O EDID anunciava PQ/ST2084, mas omitira o bit Type 1 que a função
`nvDpyIsHDRCapable()` da NVIDIA 615.78.08 exige.

## Depois da correção, aplicada manualmente fora deste projeto

O compositor registrou:

- 2560×1440 a 164,95599 Hz.
- Formato `XBGR2101010`, com 10 bits por canal de cor.
- `colorManagementPreset=hdr`.
- Ajustes SDR 2.0, 1.8, 1.5 e 1.2 aplicados em sequência.
- Retorno a `XRGB8888` e `srgb` ao término do teste temporário.

O usuário relatou ausência do congelamento completo observado antes e preferiu
prosseguir com brilho SDR 1.5. Não foi medida a luminância nem a fidelidade de
cores. A preferência de brilho não é uma calibração universal.

## Firefox/YouTube

As estatísticas de reprodução informaram VP9 Profile 2 de 10 bits, formato
YouTube 337, 3840×2160 a 60 fps e cor `smpte2084 (PQ) / bt2020`.
Isso confirma o conteúdo HDR recebido, não a correção da apresentação física.
O usuário relatou vídeo lavado; a comparação com um player independente ainda
não foi concluída. Não há diagnóstico final para essa etapa.

## Estado do projeto

O repositório oferece diagnóstico por leitura e geração de uma cópia offline.
Não contém os scripts experimentais que alteraram a saída ou instalaram o
firmware. Publicar este resumo não significa que instalação persistente,
calibração, Firefox ou compatibilidade com outros dispositivos estejam validados.
