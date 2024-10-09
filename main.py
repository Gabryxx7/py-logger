import threading


class Singleton:
    def __init__(self, cls):
        self._cls = cls
        self._lock = threading.Lock()

    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            with self._lock:
                # another thread could have created the instance
                # before we acquired the lock. So check that the
                # instance is still nonexistent.
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
        self.global_tag = ""
        
    def __call__(self, **kwargs):
        return self.d(**kwargs)

    def add_widget(self, widget):
        for log_w in self.widgets:
            if log_w.tag == widget.tag:
                print(f"Log Widget {widget.tag} already added!")
                return
        print(f"Adding Log Widget {widget.tag}")
        self.widgets.append(widget)
        return self

    def set_global_tag(self, tag):
        self.global_tag = tag

    def w(self, text, tag=None, **kwargs):
        return self.append(text, tag, 'w', **kwargs)

    def d(self, text, tag=None, **kwargs):
        return self.append(text, tag, 'd', **kwargs)

    def e(self, text, tag=None, **kwargs):
        return self.append(text, tag, 'e', **kwargs)

    def s(self, text, tag=None, **kwargs):
        return self.append(text, tag, 's', **kwargs)

    def i(self, text, tag=None, **kwargs):
        return self.append(text, tag, 'i', **kwargs)

    def append(self, text, tag=None, log_level='a', **kwargs):
        tag = self.global_tag if tag is None else tag
        pos = 0
        for widget in self.widgets:
            res = widget.append(text, tag, log_level, **kwargs)
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
