# Projeto

Montar um videogame portátil com o formato de um gameboy advance utilizando um Raspberry Pi Zero 2W.

## Componentes
- Raspberry Pi Zero 2W
- Gameboy Advance Case
- Bateria de lítio (1000mAh 3.7v)
- Botão de ligar/desligar (power switch)
- Módulo de carregamento de bateria (5v)
- Entrada USB tipo C
- Tela LCD TFT 2.8'' (240x320)
- Alto falante
- Amplificador de alto falante I²S
- Conector de fone de ouvido

## Circuito

![Circuito](assets/circuit.png)

---

# Configurações

## Sistema operacional

O sistema operacional usado será o [retropie](https://retropie.org.uk/). Siga a instalação normalmente com base no tutorial disponibilizado pelo site.

## Configuração de tela LCD

- [Driver para tela LCD (ILI9341)](https://github.com/juj/fbcp-ili9341)

Adicione a configuração de tela no arquivo `/boot/config.txt`:

```diff
-hdmi_group=2
+hdmi_group=2
+hdmi_mode=87
+hdmi_cvt=320 240 60 1 0 0 0 # Configuração para tela 320x240
+hdmi_force_hotplug=1

-dtparam=i2c_arm=on
+#dtparam=i2c_arm=on
-dtparam=i2s_arm=on
+#dtparam=i2s_arm=on
-dtparam=spi=on
+#dtparam=spi=on
```

Instalação do driver:

> [!WARNING]
> Nesse exemplo `GPIO5` e `GPIO6` serão usados para comunicação com a tela LCD. Mude o número dos _gpio_ se a sua configuração for diferente.

```bash
# Instalação
sudo apt install cmake
cd ~
git clone https://github.com/juj/fbcp-ili9341.git
cd fbcp-ili9341
mkdir build
cd build
cmake -DILI9341=ON -DGPIO_TFT_DATA_CONTROL=5 -DGPIO_TFT_RESET_PIN=6 -DSPI_BUS_CLOCK_DIVISOR=6 -DSTATISTICS=0 -USE_DMA_TRANSFERS=ON ..
make -j

# Teste a tela
sudo ./fbcp-ili9341
```

Para deixar a tela sempre ligada, adicione a seguinte linha no `/etc/rc.local`:

```bash
# Inicializar driver de tela
sudo /home/pi/fbcp-ili9341/build/fbcp-ili9341 &
```

### Configuração de áudio

Adicione a configuração de inicialização de áudio no arquivo `/boot/config.txt`:

```diff
-dtparam=audio=on
+#dtparam=audio=on
+dtoverlay=hifiberry-dac
+dtoverlay=i2s-mmap
```

Crie o arquivo `/etc/asound.conf` com a configuração do driver de áudio:

```bash
pcm.hifiberry {
	type hw card 0
}

pcm.dmixer {
	type dmix
	ipc_key 1024
	ipc_perm 0666
	slave {
		pcm "hifiberry"
		period_time 0
		period_size 1024
		buffer_size 8192
		rate 44100
		channels 2
	}
}

ctl.dmixer {
	type hw card 0
}

pcm.softvol {
	type softvol
	slave.pcm "dmixer"
	control.name "PCM"
	control.card 0
}

ctl.softvol {
	type hw card 0
}

pcm.!default {
	type plug
	slave.pcm "softvol"
}
```

Teste o áudio com o comando:
```bash
speaker-test -c2 --test=wav -w /usr/share/sounds/alsa/Front_Center.wav
```

Configurações de áudio no sistema **RetroPie**:

- Audio card: `DEFAULT`
- Audio device: `PCM`
- OMX player audio device: `BOTH`

## Configuração de controle
- [Driver para configuração de controles (GPIOnext)](https://github.com/mholgatem/GPIOnext)

Usando o comando `gpio config` é possível configurar os botões do controle. Segue lista de botões disponíveis de acordo com o circuito:
- Dpad UP (`pin 5`)
- Dpad DOWN (`pin 8`)
- Dpad LEFT (`pin 3`)
- Dpad RIGHT (`pin 10`)
- Start (`pin 13`)
- Select (`pin 15`)
- A (`pin 36`)
- B (`pin 37`)
- Left Trigger 1 (`pin 11`)
- Right Trigger 1 (`pin 33`)

---

# Configurações avançadas

## Controle de áudio

Para configuração de áudio, devemos criar dois comandos no GPIOnext com `gpionext config`:

**Aumentar vôlume:**
```bash
/usr/bin/amixer -q -c 0 sset PCM 5%+
```

**Diminuir vôlume:**
```bash
/usr/bin/amixer -q -c 0 sset PCM 5%-
```

Nesse exemplo, os botões para as ações serão:
- **Select** (`pin 15`) + **RIGHT** (`pin 10`): Aumentar volume
- **Select** (`pin 15`) + **LEFT** (`pin 3`): Diminuir volume

## Controle de brilho de tela

Se a tela tem a opção de controle de brilho (_backlight_) é possível configurar um GPIO para:
- Durante iniciação de sistema ligar brilho
- Durante desligamento de sistema desligar o brilho
- Diminuir brilho em caso de inatividade

> [!WARNING]
> Nesse exemplo serão usados para ajuste de brilho da tela LCD o `GPIO12`. Mude o número do _gpio_ se a sua configuração for diferente.

1. Instale a biblioteca WiringPi:

```bash
# Instalação da biblioteca
cd ~
git clone https://github.com/WiringPi/WiringPi.git
cd WiringPi
sudo ./build

# Teste da biblioteca
gpio -v
```

2. Crie o _script_ de ajuste de brilho:

O caminho será **home/pi/scripts/screen.py** e o conteúdo deve ser o mesmo do arquivo [extras/screen.py](extras/screen.py)

3. Adicione o arquivo que salvará o valor de brilho no sistema:

```bash
echo "1024" > /home/pi/scripts/screen.log
```

4. Ajuste o arquivo de `/etc/rc.local` para inicializar as configurações de brilho:

```diff
# Inicializar driver de tela
sudo /home/pi/fbcp-ili9341/build/fbcp-ili9341 &

+#Inicializar brilho de tela
+python3 /home/pi/scripts/screen.py -q init
```

5. Adicione os comandos de ajuste de brilho no GPIOnext:

```bash
gpionext config
```

**Aumentar brilho:**
```bash
python3 /home/pi/scripts/screen.py -q increment
```

**Diminuir brilho:**
```bash
python3 /home/pi/scripts/screen.py -q decrement
```

Nesse exemplo, os botões para as ações serão:
- **Select** (`pin 15`) + **UP** (`pin 5`): Aumentar brilho
- **Select** (`pin 15`) + **DOWN** (`pin 8`): Diminuir brilho

6. (OPCIONAL) Adicione as seguintes linhas no arquivo `/boot/config.txt` desligar o brilho de tela ao desligar o console:

```bash
# Setup backlight control pin to output mode with LOW value
dtoverlay=gpio-poweroff,active_low,gpiopin=12,timeout_ms=100
gpio=12=op,dl,pn
```

> É possível que os comandos já estejam mapeados para outra ação no _retroach_, se for o caso, edite o comando conflitante no arquivo `/opt/retropie/configs/all/retroarch-joypads/GPIOnext Joypad 1.cfg`

---

# Metas

Etapas para finalização do projeto:

- [x] Configuração de tela LCD
- [x] Configuração de energia
	- [x] Conectar entrada USB para carregamento de bateria
	- [x] Conectar botão de ligar/desligar
	- [x] Conectar bateria de lítio ao circuito
- [x] Configuração de som
	- [x] Habilitar som do alto falante
	- [x] Habilitar som do conector de fone
	- [x] Configurar troca de fonte de som de acordo com fone conectado
	- [x] Configurar controle de volume
- [x] Configuração dos controles
	- [x] Criar circuito dos botões e Dpad
	- [x] Configurar controle de som
	- [x] Configurar controle de brilho

---

# Referências

- [Game Boy Zero](https://beardedmaker.com/wiki/index.php?title=Game_Boy_Zero)
- [DIY Raspi Zero Inside a GBA](https://www.reddit.com/r/raspberry_pi/comments/14h64eg/diy_raspi_zero_inside_a_gba)
- [Raspberry Pi Pinout](https://pinout.xyz/)
