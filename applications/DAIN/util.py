import os, sys
import glob
import shutil
import cv2


class AverageMeter(object):
    """Computes and stores the average and current value"""
    def __init__(self):
        self.reset()

    def reset(self):
        self.val = 0
        self.avg = 0
        self.sum = 0
        self.count = 0

    def update(self, val, n=1):
        self.val = val
        self.sum += val * n
        self.count += n
        self.avg = self.sum / self.count


def combine_frames(input, interpolated, combined, num_frames):
    frames1 = sorted(glob.glob(os.path.join(input, '*.png')))
    frames2 = sorted(glob.glob(os.path.join(interpolated, '*.png')))
    num1 = len(frames1)
    num2 = len(frames2)
    # assert (num1 - 1) * num_frames == num2
    for i in range(num1):
        src = frames1[i]
        imgname = int(src.split('/')[-1].split('.')[-2])
        assert i == imgname
        dst = os.path.join(combined, '{:08d}.png'.format(i * (num_frames + 1)))
        shutil.copy2(src, dst)
        if i < num1 - 1:
            try:
                for k in range(num_frames):
                    src = frames2[i * num_frames + k]
                    dst = os.path.join(
                        combined,
                        '{:08d}.png'.format(i * (num_frames + 1) + k + 1))
                    shutil.copy2(src, dst)
            except Exception as e:
                print(e)
                print(len(frames2), num_frames, i, k, i * num_frames + k)


def remove_duplicates(paths):
    def dhash(image, hashSize=8):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (hashSize + 1, hashSize))
        diff = resized[:, 1:] > resized[:, :-1]
        return sum([2**i for (i, v) in enumerate(diff.flatten()) if v])

    hashes = {}
    imagePaths = sorted(glob.glob(os.path.join(paths, '*.png')))
    for imagePath in imagePaths:
        image = cv2.imread(imagePath)
        h = dhash(image)
        p = hashes.get(h, [])
        p.append(imagePath)
        hashes[h] = p

    for (h, hashedPaths) in hashes.items():
        if len(hashedPaths) > 1:
            for p in hashedPaths[1:]:
                os.remove(p)

    frames = sorted(glob.glob(os.path.join(paths, '*.png')))
    for fid, frame in enumerate(frames):
        new_name = '{:08d}'.format(fid) + '.png'
        new_name = os.path.join(paths, new_name)
        os.rename(frame, new_name)

    frames = sorted(glob.glob(os.path.join(paths, '*.png')))
    return frames
