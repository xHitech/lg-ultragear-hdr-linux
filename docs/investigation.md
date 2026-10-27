# Minha investigação do HDR

Meu ambiente: Arch Linux, NVIDIA RTX 4060 Ti, nvidia-open/NVIDIA 615.78.08,
Hyprland 0.56.2, Aquamarine 0.15.1 e Firefox 158.0.1.

Reuni aqui os resultados da investigação do meu monitor, feita com assistência
do Codex. Selecionei os dados técnicos necessários e deixei de fora endereços de
rede, credenciais, URLs assinadas, cookies e dumps de memória.

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

O EDID do meu monitor anunciava PQ/ST2084, mas omitira o bit Type 1 que a função
`nvDpyIsHDRCapable()` da NVIDIA 615.78.08 exige.

## Depois que apliquei a correção manualmente

Os logs dos meus testes registraram:

- 2560×1440 a 164,95599 Hz.
- Formato `XBGR2101010`, com 10 bits por canal de cor.
- `colorManagementPreset=hdr`.
- Ajustes SDR 2.0, 1.8, 1.5 e 1.2 aplicados em sequência.
- Retorno a `XRGB8888` e `srgb` ao término do teste temporário.

Não tive o congelamento completo observado antes e escolhi continuar os testes
com brilho SDR 1.5. Ainda não medi a luminância nem a fidelidade de cores.
Esse ajuste é minha preferência de uso, não uma calibração universal.

## Firefox/YouTube

As estatísticas de reprodução informaram VP9 Profile 2 de 10 bits, formato
YouTube 337, 3840×2160 a 60 fps e cor `smpte2084 (PQ) / bt2020`.
Isso confirma o conteúdo HDR recebido, não a correção da apresentação física.
Percebi a imagem do vídeo mais lavada ao habilitar HDR no Firefox. Ainda não
concluí a comparação com um player independente; por isso, não fechei o
diagnóstico dessa etapa.

## Estado do projeto

Nesta versão, publiquei o diagnóstico por leitura e a geração de uma cópia
offline. Mantive fora do repositório os scripts experimentais que usei para
alterar a saída ou instalar o override. Ainda preciso validar instalação
persistente, calibração, Firefox e compatibilidade com outros dispositivos.
