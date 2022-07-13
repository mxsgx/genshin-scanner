import argparse
from datetime import datetime
from email.policy import default
from glob import glob
import json
import logging
import os
import sys
from time import sleep
from typing import List, Optional, Tuple
import warnings
import cv2
import numpy as np
import easyocr
from easyocr import Reader

warnings.filterwarnings('ignore', category=UserWarning)


class GenshinScanner:
    log_id: Optional[str]
    logger: Optional[logging.Logger]
    debug: bool = False
    templates: List = []
    template_names: List[str] = []
    materials_scanned: List[str] = []

    def __init__(self, ocr: Reader, container_height: int = 17, threshold: float = 0.75, debug=False):
        self.container_height = container_height
        self.debug = debug
        self.ocr = ocr
        self.threshold = threshold

        self.log_id = f'{datetime.now().strftime("%Y-%m-%d")}-{os.getpid()}'

        logs_path = os.path.realpath(f'./logs/{self.log_id}.log')
        logs_dir_path = os.path.dirname(logs_path)

        if not os.path.exists(logs_dir_path):
            os.makedirs(logs_dir_path)

        logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s', handlers=[
            logging.FileHandler(logs_path, 'w'),
            logging.StreamHandler(sys.stdout)
        ], level=logging.NOTSET)

        self.logger = logging.getLogger()

        with open(os.path.join(os.path.dirname(__file__), 'materials.json'), 'r') as file:
            self.materials: dict = json.load(file)

        for path in glob(os.path.join(os.path.dirname(__file__), 'templates', '*.png')):
            name = os.path.basename(path).replace('.png', '')

            self.template_names.append(name)
            self.templates.append(cv2.imread(path))

    def scan(self, img_path: str, delay: Optional[float] = 1, bulk: bool = False):
        if delay is not None:
            sleep(delay)

        img_real_path = os.path.realpath(img_path)
        img = cv2.imread(img_path)

        self.logger.info(f'Scanning {img_real_path}')

        materials: List[Tuple[Optional[str],
                              Optional[str], Optional[int]]] = []

        for name, template in zip(self.template_names, self.templates):
            if bulk and name in self.materials_scanned:
                continue

            result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)

            (y_coords, x_coords) = np.where(result >= self.threshold)

            for start_x, start_y in zip(x_coords, y_coords):
                end_x = start_x + template.shape[1]
                end_y = start_y + template.shape[0] + self.container_height
                _start_y = end_y - self.container_height - 2

                self.logger.info(
                    f'Detected item "{self.materials[name]}" at [[{start_x}, {start_y}], [{end_x}, {end_y}]]')

                crop = img[_start_y:end_y, start_x:end_x]

                if self.debug:
                    tmp_img_path = os.path.realpath(
                        f'./temp/{self.log_id}/{name}.png')
                    tmp_img = img[start_y:end_y, start_x:end_x]

                    if not os.path.exists(os.path.dirname(tmp_img_path)):
                        os.makedirs(os.path.dirname(tmp_img_path))

                    cv2.imwrite(tmp_img_path, tmp_img)

                    self.logger.info(f'Evidence image File at {tmp_img_path}')

                read = self.ocr.recognize(
                    crop,
                    detail=0,
                    allowlist='0123456789'
                )

                if len(read) > 0:
                    qty = int(read[0])

                    self.logger.info(
                        f'Recognize item "{self.materials[name]}" quantity with value: {qty}')

                    materials.append((self.materials[name], name, qty))
                else:
                    self.logger.warn(
                        f'Cannot recognize item "{self.materials[name]}" quantity')

                    materials.append((self.materials[name], name, 0))

                break

        self.logger.info(
            f'Found total {len(materials)} item in {img_real_path}')

        return materials

    def scans(self, img_paths: List[str], delay: float = 1):
        self.materials_scanned.clear()

        results: List[List[Tuple[Optional[str],
                                 Optional[str], Optional[int]]]] = []

        for img_path in img_paths:
            scan = self.scan(img_path, bulk=True, delay=delay)

            results.append(scan)

        return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Scans your Genshin Impact inventory and save as GOOD format.')

    parser.add_argument('scan', nargs=1, metavar="SOURCE", type=str,
                        help="file path or glob pattern if using bulk mode")
    parser.add_argument('-o', '--output', nargs=1, metavar="DESTINATION", type=str,
                        help="the destination output file", default=['output.good'])
    parser.add_argument('-d', nargs=1, metavar="SECONDS",
                        type=int, help='delay process to reduce cpu, gpu, and memory usage', required=False, default=2)
    parser.add_argument('--no-delay', help='disable delay but increase cpu, gpu, and memory usage',
                        required=False, default=False, action='store_true')
    parser.add_argument('--bulk', type=bool, help='set scan mode to bulk/multiple images',
                        required=False, default=False, action=argparse.BooleanOptionalAction)

    args = parser.parse_args()

    ocr = easyocr.Reader(lang_list=['ch_sim', 'en'], verbose=False)
    scanner = GenshinScanner(ocr, threshold=0.81, debug=False)

    if args.bulk:
        pages = scanner.scans(
            glob(args.scan[0]), delay=None if args.no_delay else args.d)
    else:
        pages = scanner.scan(
            args.scan[0], delay=None if args.no_delay else args.d)

    good = {
        'format': 'GOOD',
        'version': 2,
        'source': 'Genshin Scanner',
        'materials': {}
    }

    if scanner.logger:
        scanner.logger.info(
            f'Generating GOOD (Genshin Open Object Description) file...')

    if args.bulk:
        for page in pages:
            for material, name, value in page:
                good['materials'][name] = value
    else:
        for material, name, value in pages:
            good['materials'][name] = value

    output_path = os.path.realpath(args.output[0])

    with open(output_path, 'w+') as file:
        file.write(json.dumps(good, indent=4))

        if scanner.logger:
            scanner.logger.info(f'File saved to {output_path}')
