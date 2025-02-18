from PIL import Image
import numpy as np
from perlin_numpy import generate_fractal_noise_2d, generate_perlin_noise_2d
import streamlit as st
import random

def get_noise(type='perlin'):    
    if type == 'fractal':
        return generate_fractal_noise_2d((sizex, sizey), (4, 4), 5)
    elif type == 'perlin':
        return generate_perlin_noise_2d((sizex, sizey), (4, 4))

def create_img(noise):
    img = Image.new('RGB', (sizex, sizey), color='white')
    bin_arr = np.zeros((sizex, sizey))
    for i in range(sizex):
        for j in range(sizey):
            if noise[i, j] < water_mod:
                bin_arr[i, j] = 0
                img.putpixel((i, j), (56, 56, 200))
            elif noise[i, j] > mountain_mod:
                bin_arr[i, j] = 2
                img.putpixel((i, j), (100, 45, 80))
            else:
                bin_arr[i, j] = 1
                img.putpixel((i, j), (56, 150, 56))

    return img, bin_arr

def get_img_in_bytes():
    from io import BytesIO
    buf = BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

def generate_voronoi_regions(land_map, num_nations=7):
    img2 = img.copy()
    land_positions = np.argwhere(land_map >= 1)

    nation_centers = land_positions[np.random.choice(len(land_positions), num_nations, replace=False)]
    region_colors = {i: (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) for i in range(num_nations)}
    
    point_to_region = {}
    for i, center in enumerate(nation_centers):
        point_to_region[tuple(center)] = i

    noise_map = get_noise(type='fractal')
    for x in range(sizex):
        for y in range(sizey):
            if land_map[x, y] > 0:
                perturb_x = (noise_map[x, y] - 0.5) * 70
                perturb_y = (noise_map[y, x] - 0.5) * 70

                closest_center = min(
                    nation_centers, 
                    key=lambda c: ((c[0] + perturb_x - x) ** 2 + (c[1] + perturb_y - y) ** 2)
                )
                
                region = point_to_region[tuple(closest_center)]
                color = region_colors[region]
                img2.putpixel((x, y), color)
            else:
                img2.putpixel((x, y), (56, 56, 200))

    return img2

if __name__ == '__main__':
    sizex: int = 1024
    sizey: int = 1024

    st.header('Map generation')
    water_mod: float = st.slider('Water level', -1.0, 1.0, 0.0, 0.01)
    mountain_mod: float = st.slider('Mountain level', water_mod, 1.0, (water_mod+1)/2, 0.01)

    if st.button('Generate'):
        noise = get_noise('fractal')
        img, bin_arr = create_img(noise)

        nations_img = generate_voronoi_regions(bin_arr)

        st.image(nations_img, use_container_width=True)
        st.image(img, use_container_width=True)


        byte_im = get_img_in_bytes()
        st.download_button("Download", byte_im, file_name="map.jpg")

