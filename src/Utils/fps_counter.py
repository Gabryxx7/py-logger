import time

class FPSCounter():
  def __init__(self, reset_time=10):
    self.reset_time = reset_time
    self.fps = 0
    self.frame_count = 0
    self.start_time = 0
    self.last_frame_time = time.time()

  def reset(self):
    self.frame_count = 0
    self.start_time = time.time()
    self.last_frame_time = time.time()

  def time_since_last_update(self):
    return time.time() - self.last_frame_time

  def update(self, new_frames=0):
    if new_frames > 0:
      self.frame_count += new_frames
      self.last_frame_time = time.time()
    elapsed = time.time() - self.start_time
    if elapsed > 0:
      self.fps = int(self.frame_count / (elapsed))
      if elapsed >= self.reset_time:
        self.reset()