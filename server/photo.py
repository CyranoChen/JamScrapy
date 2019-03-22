# -*- coding: utf-8 -*-
import os
import json
import cv2
import base64
import numpy as np

from matplotlib import pyplot as plt

import config

MARGIN = 0.4


def generate_face(file_path, coordinate):
    file_ext_name = file_path.split('.')[-1].lower()
    print(file_path, coordinate)
    if os.path.isfile(file_path) and file_ext_name in ['jpg', 'jpeg', 'png', 'bmp']:
        img = cv2.imread(file_path, 1)
        if img is not None:
            # input_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            cropped = crop_face(img, coordinate, margin=MARGIN)
            return cropped, img

    return None, None


def generate_photo(file_path, faces):
    file_ext_name = file_path.split('.')[-1].lower()
    print(file_path, len(faces))
    if os.path.isfile(file_path) and file_ext_name in ['jpg', 'jpeg', 'png', 'bmp']:
        img = cv2.imread(file_path, 1)
        img_h, img_w, _ = np.shape(img)
        if img is not None:
            face_imgs = []
            for f in faces:
                cropped = crop_face(img, f['coordinate'], margin=MARGIN)
                if f['username'] is not None:
                    draw_label(img, point=(f['coordinate'][0], f['coordinate'][1]),
                               label="{} {} {:.2}".format(f['id'], f['username'], f['confidence']))
                face_imgs.append(cropped)

            return face_imgs, img

    return None, None


def crop_face(image, coord, margin, rectangle=True):
    img_h, img_w, _ = np.shape(image)
    x1, y1, x2, y2 = coord
    w, h = x2 - x1, y2 - y1
    xw1 = max(int(x1 - margin * w), 0)
    yw1 = max(int(y1 - margin * h), 0)
    xw2 = min(int(x2 + margin * w), img_w - 1)
    yw2 = min(int(y2 + margin * h), img_h - 1)

    if rectangle:
        cv2.rectangle(image, (x1, y1), (x2, y2), (255, 0, 0), 2)

    return image[yw1:yw2, xw1:xw2, :]


def draw_label(image, point, label, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.8, thickness=1):
    size = cv2.getTextSize(label, font, font_scale, thickness)[0]
    x, y = point
    cv2.rectangle(image, (x, y - size[1]), (x + size[0], y), (255, 0, 0), cv2.FILLED)
    cv2.putText(image, label, point, font, font_scale, (255, 255, 255), thickness, lineType=cv2.LINE_AA)


def cvimg_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    ret_val = base64.b64encode(buffer)

    return ret_val


if __name__ == '__main__':
    file_path = './cache/IMGM7027.JPG'
    coord = [1322, 1406, 1430, 1514]

    face, img = generate_face(file_path, coord)
    cv2.imwrite('./cache/IMGM7027_REC.JPG', img)

    print('face', face.shape)
    print(str(cvimg_to_base64(face), encoding='utf-8'))
    plt.imshow(face[:, :, ::-1])
    plt.show()

    print('img_raw', img.shape)
    plt.imshow(img[:, :, ::-1])
    plt.show()

    sql = f'''
              select * from face_extraction where 
              filepath = '/Volumes/Storage/dataset/d-kom_photo/dkom2019/展台/IMGM7027.JPG'
           '''

    results = config.ENGINE.execute(sql).fetchall()
    results = [{'id': r.id, 'username': r.username, 'confidence': r.confidence, 'coordinate': json.loads(r.coordinate)}
               for r in results]

    faces, img = generate_photo(file_path, results)
    cv2.imwrite('./cache/IMGM7027_REC.JPG', img)

    print(len(faces))

    print("done")
