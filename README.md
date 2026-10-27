# LG UltraGear HDR on Linux

Ferramentas de diagnóstico por leitura e correção **offline** do EDID de monitores
LG identificados como **GSM 0x7766**. Projeto experimental, independente da LG,
NVIDIA, Mozilla e Hyprland.

## Escopo desta versão

A ferramenta lê o EDID e pode escrever uma **nova cópia** com o bit de metadados
HDR Type 1 corrigido. Não instala essa cópia, não ativa HDR, não executa `sudo`,
não troca modos de vídeo e não modifica firmware físico, drivers ou boot.
Os comandos recusam execução como root e não sobrescrevem arquivos existentes.

Não há promessa de risco zero para instalações ou alterações futuras. Qualquer
etapa que altere o sistema está fora desta versão e exigirá análise separada.

## Problema investigado

Um LG GSM 0x7766 anunciava PQ/ST2084 no EDID, mas não o descritor Static Metadata
Type 1. Na NVIDIA 615.78.08, `nvDpyIsHDRCapable()` verifica explicitamente esse
descritor. Sem ele, a ativação de HDR/BT2020 pode ser recusada pelo driver.

A correção muda somente o bit ausente e o checksum da extensão CTA. Mantém os
modos, frequências, primárias, luminâncias e demais dados do EDID original.
Não é um patch universal: o programa recusa outros identificadores, ausência de
PQ, checksums inválidos, dados truncados e múltiplos blocos HDR ambíguos.

### Evidências e limites

Em uma máquina com Arch Linux, RTX 4060 Ti, NVIDIA 615.78.08, Hyprland 0.56.2 e
Aquamarine 0.15.1, o override corrigido permitiu configurar a saída em
2560×1440 a aproximadamente 165 Hz, formato de 10 bits e preset HDR. O usuário
relatou que o congelamento completo anterior deixou de ocorrer nesse teste.
Isso **não comprova calibração ou fidelidade física de cores**.

A reprodução HDR no Firefox 158/YouTube continua em investigação. Receber PQ e
BT.2020 do serviço não comprova que toda a cadeia esteja reproduzindo as cores
corretamente. Ajustar saturação para esconder uma falha não faz parte da solução.
Os patches experimentais de Aquamarine não são necessários para executar este
projeto e não estão incluídos nesta versão.

## Executar sem instalação

Python 3.10 ou superior. Não são necessárias dependências Python externas.
Execute como usuário comum, na pasta do projeto:

```bash
python3 -m lg_hdr doctor
```

O diagnóstico mostra as saídas conectadas, checksums e descritores HDR. Não
mostra números de série nem inclui os bytes completos do EDID no relatório.
Hashes identificam o conteúdo e também devem ser revisados antes de compartilhar.

Inspecionar um arquivo local:

```bash
python3 -m lg_hdr inspect /caminho/para/original.bin
```

Gerar uma cópia corrigida, sem instalar ou aplicar:

```bash
python3 -m lg_hdr patch /caminho/para/original.bin ./corrigido.bin
```

O destino precisa estar dentro da home do usuário ou de `/tmp`, e não pode
existir. O EDID original não é modificado. Um arquivo que já anuncia Type 1 é
copiado sem novas alterações. **Os EDIDs reais incluídos em `examples/edid/` foram autorizados pelo proprietário.**
Eles podem conter números de série. Não envie EDIDs de terceiros sem autorização;
use os testes sintéticos para contribuir.

A validação implementada cobre estrutura, limites dos blocos e checksums; não é
um validador completo de conformidade EDID. Um checksum válido não garante que
todas as características anunciadas pelo fabricante estejam corretas.

## Testes automatizados

```bash
python3 -m unittest discover -s tests -v
```

Os testes usam arquivos temporários e EDIDs sintéticos, sem GPU, monitor, acesso
root ou alteração do sistema. Cobrem correção restrita ao modelo, preservação dos
bytes, idempotência, corrupção, ambiguidades, proteção de arquivos e diagnóstico.
O CI também só executa testes offline. Há um teste adicional dos dois EDIDs reais
autorizados em `examples/edid/`, sem acesso a hardware.

## Desenvolvimento

- [x] Inspeção de EDID e detecção de PQ/Type 1.
- [x] Correção offline com checksums recalculados.
- [x] Testes sintéticos e CI.
- [ ] Investigar Firefox/Hyprland com referência HDR independente.
- [ ] Documentar separadamente uma eventual instalação persistente e reversível.
- [ ] Validar instalação e recuperação em ambiente de teste antes de distribuí-las.

## Fontes

- [Verificação HDR na NVIDIA 615.78.08](https://github.com/NVIDIA/open-gpu-kernel-modules/blob/615.78.08/src/nvidia-modeset/src/nvkms-dpy.c)
- [Patch publicado para o Type 1 ausente em GSM 0x7766](https://www.mail-archive.com/dri-devel%40lists.freedesktop.org/msg630093.html)
- [Documentação de overrides EDID do kernel](https://www.kernel.org/doc/html/latest/admin-guide/edid.html)
- [Investigação de vídeo no Firefox 158/Wayland](https://bugzilla.mozilla.org/show_bug.cgi?id=2083037)

## Licença

MIT para o código original deste projeto. As fontes externas são referências;
não há cópia de drivers NVIDIA, código do Firefox ou bibliotecas de terceiros.

## Exemplos reais autorizados

[Origem, checksums e limites dos exemplos](examples/edid/README.md).
[Resumo técnico dos testes locais](docs/investigation.md). Dumps de memória não
são publicados; logs completos precisam de revisão antes de inclusão.
