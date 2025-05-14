from bokeh.plotting import figure, curdoc
from bokeh.layouts import column, row
from bokeh.models import Slider, CheckboxGroup, Button
import numpy as np
from scipy.signal import butter, filtfilt
import sys
import subprocess

# Initial values for sliders
amp_init = 1.0
freq_init = 0.5
phase_init = 0.0
noise_mean_init = 0.0
noise_cov_init = 0.1
global_noise = None

# Time axis creation
time = np.linspace(0, 10, 1000)
sampling_rate = 1 / (time[1] - time[0])

# Harmonic signal generation
def generate_harmonic(time, amplitude, frequency, phase):
    return amplitude * np.sin(2 * np.pi * frequency * time + phase)

# Noise generation
def generate_noise(time, noise_mean, noise_cov):
    return np.random.normal(noise_mean, np.sqrt(noise_cov), len(time))

# Harmonic signal with noise
def harmonic_with_noise(time, amplitude, frequency, phase=0, noise_mean=0, noise_cov=0.1, noise=None):
    harmonic_signal = generate_harmonic(time, amplitude, frequency, phase)
    if noise is not None:
        return harmonic_signal + noise
    else:
        global global_noise
        global_noise = generate_noise(time, noise_mean, noise_cov)
        return harmonic_signal + global_noise

# Median filter
def apply_median_filter(data, window_size):
    filtered_data = []
    window_size = int(window_size)
    for i in range(len(data)):
        if i < window_size // 2:
            window = data[:i + window_size]
        elif i >= len(data) - window_size // 2:
            window = data[i - window_size + 1:]
        else:
            window = data[i - window_size // 2:i + window_size // 2 + 1]
        filtered_data.append(sorted(window)[window_size // 2])
    return filtered_data

# GUI plot setup
plot = figure(title="Harmonic & Noise", x_axis_label='Time', y_axis_label='Amplitude', width=1000, height=500, align='center', sizing_mode="fixed", toolbar_location="below")

# Harmonic signal plot
harmonic_line = plot.line(time, generate_harmonic(time, amp_init, freq_init, phase_init), line_width=2, color='cyan', line_dash='dotted', legend_label='Harmonic line')

# Signal with noise plot
noise_line = plot.line(time, harmonic_with_noise(time, amp_init, frequency=freq_init, phase=phase_init, noise_mean=noise_mean_init, noise_cov=noise_cov_init, noise=None), 
                       line_width=2, color='royalblue', legend_label='Signal with noise')

# Filtering the noisy signal
filtered_signal = apply_median_filter(noise_line.data_source.data['y'], sampling_rate)
filtered_line = plot.line(time, filtered_signal, line_width=2, color='midnightblue', legend_label='Filtered Signal')

# Slider controls for parameters
slider_color = 'darkblue'

amplitude_slider = Slider(title="Amplitude", value=amp_init, start=0.1, end=10.0, step=0.1, bar_color=slider_color)
frequency_slider = Slider(title="Frequency", value=freq_init, start=0.1, end=10.0, step=0.1, bar_color=slider_color)
phase_slider = Slider(title="Phase", value=phase_init, start=0.0, end=2 * np.pi, step=0.1, bar_color=slider_color)
noise_mean_slider = Slider(title="Noise Mean", value=noise_mean_init, start=-1.0, end=1.0, step=0.1, bar_color=slider_color)
noise_cov_slider = Slider(title="Noise Covariance", value=noise_cov_init, start=0.0, end=1.0, step=0.1, bar_color=slider_color)
window_size_slider = Slider(title="Window Size", value=3, start=1, end=35.0, step=1, bar_color=slider_color)

show_noise_checkbox = CheckboxGroup(labels=['Show Noise'], active=[0])

regenerate_noise_button = Button(label='Regenerate Noise')

reset_button = Button(label='Reset')

# Update function triggered when slider values change
def update(attrname, old, new):
    amplitude = amplitude_slider.value
    frequency = frequency_slider.value
    phase = phase_slider.value

    noise_mean = noise_mean_slider.value
    noise_cov = noise_cov_slider.value

    global amp_init, noise_mean_init, noise_cov_init, global_noise
    
    if noise_mean_init != noise_mean or noise_cov_init != noise_cov:
        noise_mean_init = noise_mean
        noise_cov_init = noise_cov
        global_noise = generate_noise(time, noise_mean, noise_cov)

    show_noise = bool(new)
    harmonic_line.data_source.data['y'] = generate_harmonic(time, amplitude, frequency, phase)
    noise_line.data_source.data['y'] = harmonic_with_noise(time, amplitude, frequency, phase, noise_mean, noise_cov, global_noise)
    noise_line.visible = show_noise

    window_size = window_size_slider.value
    filtered_signal = apply_median_filter(noise_line.data_source.data['y'], window_size)
    filtered_line.data_source.data['y'] = filtered_signal

# Regenerate noise button
def regenerate_noise():
    noise_line.data_source.data['y'] = harmonic_with_noise(time, amplitude_slider.value, frequency_slider.value, phase_slider.value, noise_mean_slider.value, noise_cov_slider.value)

# Reset button
def reset_params():
    amplitude_slider.value = amp_init
    frequency_slider.value = freq_init
    phase_slider.value = phase_init
    noise_mean_slider.value = 0.0
    noise_cov_slider.value = 0.1
    window_size_slider.value = 3
    show_noise_checkbox.active = [0]
    regenerate_noise()

amplitude_slider.on_change('value', update)
frequency_slider.on_change('value', update)
phase_slider.on_change('value', update)
noise_mean_slider.on_change('value', update)
noise_cov_slider.on_change('value', update)
window_size_slider.on_change('value', update)

show_noise_checkbox.on_change('active', update)
regenerate_noise_button.on_click(regenerate_noise)
reset_button.on_click(reset_params)

layout = column(plot, 
                row(amplitude_slider, frequency_slider, align='center'),
                row(phase_slider, noise_mean_slider, align='center'),
                row(noise_cov_slider, window_size_slider, align='center'),
                row(show_noise_checkbox, regenerate_noise_button, reset_button, align='center'),
                sizing_mode='stretch_width',  align='center')

# Background color
layout.background = "cornflowerblue"
curdoc().add_root(layout)

# Starting a Bokeh server
if __name__ == "__main__":
    with open("bokeh_lab5.py", "w", encoding="utf-8") as f:
        f.write(__import__("inspect").getsource(sys.modules[__name__]))
    subprocess.run(["bokeh", "serve", "--show", "bokeh_lab5.py"])
