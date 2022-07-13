# Genshin Scanner

Scans your Genshin Impact inventory and save as GOOD format.

> This documentation still need improvement

## Requirements

- Python `3.9`
- CUDA Toolkit 11.6 (Optional)

## Installation / Setup

### Download Source Code

#### Using GIT

1. Cloning

   ```bash
   git clone https://github.com/mxsgx/genshin-scanner.git
   ```

2. Move to directory

   ```bash
   cd genshin-scanner
   ```

#### Download as ZIP

1. If you don't know how to download this source, you can download [here](https://github.com/mxsgx/genshin-scanner/archive/refs/heads/main.zip).
2. Extract and open folder, and then
3. Open in terminal (Command Prompt/PowerShell)

### Python Virtual Environment (Optional)

#### Create environemnt

```bash
python -m venv venv
```

#### Update `pip`

```bash
python -m pip install --upgrade pip
```

#### Activate

> Run this command every you want to using this tool for first time if using virtual environment.

- Command Prompt

```bat
venv\Scripts\activate.bat
```

- PowerShell

```pwsh
venv/Scripts/activate.ps1
```

- Linux or MacOS

```bash
source venv/bin/activate
```

### Installing Dependencies

#### Normal (CPU)

```bash
pip install -r cpu.txt
```

#### With CUDA (GPU)

```bash
pip install -r gpu.txt --extra-index-url https://download.pytorch.org/whl/cu116
```

> This will downloading package about >2GB so make sure your internet connection is stable and fast.

## Usage

```text
python scanner.py [-h] [-o DESTINATION] [-d SECONDS] [--no-delay] [--bulk | --no-bulk] SOURCE
```

### Description

```text
positional arguments:
  SOURCE                file path or glob pattern if using bulk mode

options:
  -h, --help            show this help message and exit
  -o DESTINATION,       the destination output file (default: output.good)
  --output DESTINATION
  -d SECONDS            delay process to reduce cpu, gpu, and memory usage (default: 2)
  --no-delay            disable delay but increase cpu, gpu, and memory usage
  --bulk, --no-bulk     set scan mode to bulk/multiple images (default: False)
```

### Example Usage

#### General Usage

- Process single image

```bash
python scanner.py "screenshot.png"
```

- Custom output file with `-o` option

```bash
python scanner.py -o "another.good" "screenshot.png"
```

- Process all image inside directory. Don't forget to add `--bulk` option. For example this command will scans all images with extension inside `screenshots` folder with image extension `.png`

```bash
python scanner.py --bulk "./screenshots/*.png"
```

#### Modify Delay Process

- Set delay to `5` seconds. If you don't set delay, it will automatically set delay to `2` seconds.

```bash
python scanner.py -d 5 "screenshot.png"
```

- Disable delay process. (Not recommended)

```bash
python scanner.py --no-delay "screenshot.png"
```

## Limitations

- This tool only works for image with 1280x728 resolution.
- This tool only scans materials category

## License

MIT
