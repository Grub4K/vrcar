# vrcar
VR controlled Raspberry Pi car

Initially developed using the [Freenove 4WD](<https://store.freenove.com/products/fnk0043>), a [Raspberry Pi 4 Model B 4GB](<https://www.raspberrypi.com/products/raspberry-pi-4-model-b/?variant=raspberry-pi-4-model-b-4gb>) and a [Meta Quest 3](<https://www.meta.com/de/en/quest/quest-3>)

## Usage
The client is easiest installed using [`pipx`](<https://pipx.pypa.io/>):

```shell
pipx install "vrcar[pygame,vr]"
```

These are what the available groups will be able to load:
- `pygame`
	- Window with the camera video feed
	- Keyboard controls
	- Joystick controls
- `vr`
	- Camera video feed in the headset
	- Headset rotation controls camera rotation

## License
`vrcar` is distributed under the terms of the [MIT](<https://spdx.org/licenses/MIT.html>) license.
