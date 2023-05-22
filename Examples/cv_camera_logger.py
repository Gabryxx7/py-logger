from pylogger_new import Log
from src.Widgets.opencv_widget import CvLogWidget

import cv2
import threading
import time
import datetime
import numpy as np
from sys import platform
from src.Utils.fps_counter import FPSCounter

class OpenCVCameraPlaceholder:
    def __init__(self, size, color=(0,0,0), border_size=5):
        self.color = color
        self.ready = True
        self.initialized = True
        self.size = size
        self.b_size = int(border_size)
        self.frame = np.full((size['height'], size['width'], 3), self.color, np.uint8)
        self.frame = cv2.copyMakeBorder(self.frame, top=self.b_size, bottom=self.b_size, left=self.b_size, right=self.b_size, borderType=cv2.BORDER_CONSTANT, value=[255, 255, 255])
        self.is_placeholder = True

    def get_frame(self):
        return self.frame

class OpenCVCamera:
    def __init__(self, cam_id, size, cap_param, cam_name=None, border_size=5):
        self.logger = Log.Instance()
        self.logger.add_widget(CvLogWidget(cv=cv2))
        self.size = size
        self.b_size = int(border_size)
        self.cam_id = cam_id
        self.cam_name = cam_name
        self.cap_param = cap_param
        if self.cam_name is None:
            self.cam_name = f'Camera {cam_id}'
        self.cam = None
        self.last_frame = None
        self.fps_counter = FPSCounter()
        self.thread = threading.Thread(target=self.capture_loop, args=[])
        self.thread_started = True
        self._stop = threading.Event()
        self.thread.start()
        self.initialized = False
        self.total_frames = 0
        self.last_thread_name = "None"
        self.frame_shape = [-1, -1]
        self.ready = False
        self.is_placeholder = False

    def capture_loop(self):
        res_str = f"Cap {self.cam_id}\t{self.cam_name}\t{self.thread.name}"
        try:
            self.cam = cv2.VideoCapture(self.cam_id, self.cap_param)
        except Exception as e:
            print(f"Error opening VideoCapture {self.cam_id}: {e}")
            pass
        self.initialized = True
        if self.cam is None or not self.cam.isOpened():
            print(res_str +" FAILED")
            self.thread_started = False
            self._stop.set()
            return
        self.ready = True
        print(res_str +" OPENED")
        while self.thread_started:
            self.last_thread_name = threading.current_thread().name
            if self._stop.isSet():
                break
            if self.cam is not None and self.cam.isOpened():
                rval, frame = self.cam.read()
                if frame is not None:
                    self.frame_shape = frame.shape
                    self.last_frame = self.process_frame(frame)
                    self.fps_counter.update(1)
                    self.total_frames = self.total_frames + 1 if self.total_frames < 100 else 0

                time.sleep(0.001)
        self.cam.release()

    def process_frame(self, frame):
        if frame is not None:
            frame = cv2.resize(frame, (self.size['width'], self.size['height']))
            frame = cv2.copyMakeBorder(frame, top=self.b_size, bottom=self.b_size, left=self.b_size, right=self.b_size, borderType=cv2.BORDER_CONSTANT, value=[255, 255, 255])
        return frame

    def get_frame(self, dbg_info=True):
        frame = None
        if self.last_frame is not None:
            frame = self.last_frame.copy()
            if dbg_info:
                lines = [f"Cap {self.cam_id} {self.cam_name}: {self.frame_shape[1]} x {self.frame_shape[0]}",
                         f"Frames: {self.total_frames}",
                         f"FPS: {self.fps_counter.fps:.2f} / {self.cam.get(cv2.CAP_PROP_FPS):.2f}",
                         f"{self.last_thread_name} / {threading.activeCount()}"
                         ]
                y_offset = 40
                font_scaling = 0.35
                for idx in range(0, len(lines)):
                    text_pos = (10, int(y_offset * (idx+1) * font_scaling))
                    self.logger.i("test", lines[idx], no_date=True, pos=text_pos, flush=False, font_size=font_scaling, color=(0, 255, 0), thickness=1)
                    text_pos = (10, int(y_offset * (idx+1+len(lines)) * font_scaling))
                    frame = cv2.putText(frame, lines[idx], text_pos, cv2.FONT_HERSHEY_SIMPLEX, font_scaling, (0, 255, 0), 1, cv2.LINE_AA)
                self.logger.flush(canvas=frame)
        return frame

class OpenCVCamerasManager:
    def __init__(self, cols=5, max_idx=10):
        self.title = "Cameras Preview"
        self.hd_scaling = 0.25
        self.cols = cols
        self.size = {'width': int(1280 * self.hd_scaling), 'height': int(720 * self.hd_scaling)}
        self.cameras = []
        self.max_idx = max_idx
        self.print_delay = 5
        self.last_print_time = time.time() - (self.print_delay-1)
        self.cap_param = cv2.CAP_DSHOW
        cv2.namedWindow(self.title)

    def init_cameras(self):
        devices = []
        if platform == 'win32':
            self.cap_param = cv2.CAP_DSHOW
            print(f"\nRunning on Windows {platform}: using cv2.CAP_DSHOW\n\n")
            from pygrabber.dshow_graph import FilterGraph
            graph = FilterGraph()
            devices = graph.get_input_devices()
            self.print_delay = 1
        else:
            print(f"\nRunning on MacOS {platform}: using cv2.CAP_AVFOUNDATION\n\n")
            self.cap_param = cv2.CAP_AVFOUNDATION
            self.print_delay = 1
        max_idx = self.max_idx if len(devices) <= 0 else len(devices)
        for idx in range(0, max_idx):
            cam_name = f'Camera {idx}'
            if idx < len(devices):
                cam_name = devices[idx]
            cam = OpenCVCamera(idx, self.size, self.cap_param, cam_name)
            self.cameras.append(cam)

        ### Test
        # self.cameras.append(OpenCVCameraPlaceholder(self.size, (255, 0 ,0)))
        # self.cameras.append(OpenCVCameraPlaceholder(self.size, (0, 255 ,0)))
        # self.cameras.append(OpenCVCameraPlaceholder(self.size, (0, 0 ,255)))
        # self.cameras.append(OpenCVCameraPlaceholder(self.size, (255, 0 ,0)))
        # self.cameras.append(OpenCVCameraPlaceholder(self.size, (0, 255 ,0)))

        self.placeholder = OpenCVCameraPlaceholder(self.size, (0, 0 ,0))

    def get_collage(self):
        total_frames = 0
        vstack = []
        hstack = []
        alive_threads = []
        active_cams = []
        for i in range(0, len(self.cameras)):
            cam = self.cameras[i]
            frame = None
            if cam.is_placeholder:
                active_cams.append(cam)
                frame = cam.get_frame()
            else:
                if cam.ready:
                    active_cams.append(cam)
                    frame = cam.get_frame()
                    if cam.thread.is_alive():
                        alive_threads.append(f"{cam.cam_name} {cam.thread.name} {cam.total_frames}")
                elif not cam.initialized:
                    active_cams.append(cam)
                else:
                    # Capture initialized but NOT ready, delete
                    pass
            if frame is not None:
                hstack.append(frame)
                total_frames += 1
                if len(hstack) >= self.cols:
                    vstack.append(hstack)
                    hstack = []
        self.cameras = active_cams
        ## Square up the grid
        if len(vstack) > 0 and len(hstack) > 0:
            while len(hstack) < self.cols:
                hstack.append(self.placeholder.get_frame())
        if len(hstack) > 0:
            vstack.append(hstack)
        output = None
        if len(vstack) > 0:
            try:
                hstacks = [np.hstack(h) for h in vstack]
                try:
                    output = np.vstack(hstacks)
                except Exception as e:
                    print(f"Exception Building hstack {len(hstack)} x {len(vstack)}: {e}")
            except Exception as e:
                print(f"Exception Building vstack {len(hstack)} x {len(vstack)}: {e}")

        if time.time() - self.last_print_time >= self.print_delay:
            self.last_print_time = time.time()
            print(f"{datetime.datetime.now()}\t\tGrid {total_frames} :{[len(h) for h in vstack]} \tThreads: {len(alive_threads)} / {len(self.cameras)}\t{alive_threads}", end='\n', flush=True)
        return output

    def start_loop(self):
        while True:
            try:
                output = self.get_collage()
                if output is not None:
                    cv2.imshow(self.title, output)
            except Exception as e:
                print(f"Exception displaying image: {e}")
            time.sleep(0.001)
            key = cv2.waitKey(1)
            if key == 27:  # exit on ESC
                return
            # print(f"Active threads {threading.activeCount()}", end='\r')

if __name__ == '__main__':
    manager = OpenCVCamerasManager()
    manager.init_cameras()
    manager.start_loop()
