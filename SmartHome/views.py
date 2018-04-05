import struct
from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView
#from Application.wsgi import buf

buf=None
class ColorPickerView(TemplateView):
    template_name = "color.html"

    curr_value = "#ffffff"

    def post(self, request):

       # led = LED.objects.get('LED1')


        if 'party' in request.POST:
            buf.write(struct.pack(">I", 250))
            buf.write(struct.pack(">I", 150))
            buf.write(struct.pack(">I", 50))
            buf.write(struct.pack(">I", 2))
            buf.seek(0)
        elif 'alarm' in request.POST:
            buf.write(struct.pack(">I", 250))
            buf.write(struct.pack(">I", 0))
            buf.write(struct.pack(">I",0))
            buf.write(struct.pack(">I", 3))
            buf.seek(0)
        else :
            self.curr_value = request.POST["color"]
            frequency = request.POST["frequency"]
            rgb_color = self.hex_to_rgb(self.curr_value)

            buf.write(struct.pack(">I", rgb_color[0]))
            buf.write(struct.pack(">I", rgb_color[1]))
            buf.write(struct.pack(">I", rgb_color[2]))
            buf.write(struct.pack(">I", int(frequency)))
            buf.seek(0)
        # light1 = get_light1()
        # light2 = get_light2()
        # color_dcr = light1.normalize_rgbb(list(rgb_color))
        # light1.set_duty_cycle(color_dcr[0], color_dcr[1], color_dcr[2])
        # light2.set_duty_cycle(color_dcr[0], color_dcr[1], color_dcr[2])

    def hex_to_rgb(self, value):
        """Return (red, green, blue) for the color given as #rrggbb."""
        value = value.lstrip('#')
        lv = len(value)
        return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
