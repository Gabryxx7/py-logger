class Singleton:
  def __init__(self, cls):
      self._cls = cls

  def Instance(self):
    try:
      return self._instance
    except AttributeError:
      self._instance = self._cls()
      return self._instance

  def __call__(self):
    raise TypeError('Singletons must be accessed through `Instance()`.')

  def __instancecheck__(self, inst):
    return isinstance(inst, self._cls)

@Singleton
class Log(object):
  def __init__(self):
    self.widgets = []
      
  def add_widget(self, widget):
    self.widgets.append(widget)
      
  def w(self, tag, text, **kwargs):
    return self.append(tag, text, 'w', **kwargs)

  def d(self, tag, text, **kwargs):
    return self.append(tag, text, 'd', **kwargs)

  def e(self, tag, text, **kwargs):
    return self.append(tag, text, 'e', **kwargs)

  def s(self, tag, text, **kwargs):
    return self.append(tag, text, 's', **kwargs)

  def i(self, tag, text, **kwargs):
    return self.append(tag, text, 'i', **kwargs)

  def append(self, tag, text, log_level='a', **kwargs):
    pos = 0
    for widget in self.widgets:
      res = widget.append(tag, text, log_level, **kwargs)    
      if res is not None:
        pos = res      
    return pos
    # if self.enabled:
    #     color = self.colors[color_name]
    #     color_reset = self.colors['reset']
    #     if self.log_levels[log_level] >= self.log_levels[self.min_log_level]:
    #         if self.enable_widget and log_to_widget and self.logWidget is not None:
    #             try:
    #                 final_text = timestampStr + color.color_html + " " + log_text + color_reset.color_html
    #                 self.logWidget.append(final_text + "\n")
    #             except Exception as e:
    #                 print("Exception writing to LOG Widget:" + str(e))
    #                 pass
    #         if self.enable_console:
    #             final_text = timestampStr + color.color_code + " " + log_text + color_reset.color_code
    #             print(final_text)
    #         if self.save_to_file:
    #             try:
    #                 self.file.write(timestampStr + log_text + "\n")
    #             except Exception as e:
    #                 print("Exception writing to LOG File:" +str(e))
    #                 pass
      
  def flush(self, **kwargs):
    for widget in self.widgets:
      widget.flush_lines(**kwargs)
          
  def init(self):
    for widget in self.widgets:
      widget.init()
      
  def destroy(self):
    for widget in self.widgets:
      widget.destroy()
