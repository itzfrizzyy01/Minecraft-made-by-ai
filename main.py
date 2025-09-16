from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from noise import pnoise2
import random

app = Ursina()

window.title = 'PythonCraft with Chunks'
window.borderless = False
window.exit_button.visible = True
window.fps_counter.enabled = True

# Load textures
grass_texture = load_texture('grass')
dirt_texture = load_texture('dirt')
stone_texture = load_texture('stone')
wood_texture = load_texture('wood')
leaves_texture = load_texture('leaves')

block_dict = {
    'grass': grass_texture,
    'dirt': dirt_texture,
    'stone': stone_texture,
    'wood': wood_texture,
    'leaves': leaves_texture
}

current_texture = grass_texture

CHUNK_SIZE = 20
RENDER_DISTANCE = 2  # How many chunks around player to render

# Dictionary to hold all loaded chunks
loaded_chunks = {}

# Voxel block definition
class Voxel(Button):
    def __init__(self, position=(0,0,0), texture=grass_texture):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture=texture,
            color=color.white,
            scale=1
        )

    def input(self, key):
        global current_texture
        if self.hovered:
            if key == 'left mouse down':
                voxel = Voxel(position=self.position + mouse.normal, texture=current_texture)
            if key == 'right mouse down':
                destroy(self)

# Generate a chunk at given chunk coordinates
def generate_chunk(chunk_x, chunk_z):
    blocks = []
    for x in range(CHUNK_SIZE):
        for z in range(CHUNK_SIZE):
            world_x = chunk_x * CHUNK_SIZE + x
            world_z = chunk_z * CHUNK_SIZE + z
            y = int(pnoise2(world_x * 0.1, world_z * 0.1, octaves=4) * 4)
            block_type = random.choice(['grass', 'dirt', 'stone'])
            texture = block_dict[block_type]
            block = Voxel(position=(world_x, y, world_z), texture=texture)
            blocks.append(block)
    return blocks

# Load chunks around the player
def load_chunks(player_chunk_x, player_chunk_z):
    global loaded_chunks
    new_chunks = {}
    for dx in range(-RENDER_DISTANCE, RENDER_DISTANCE+1):
        for dz in range(-RENDER_DISTANCE, RENDER_DISTANCE+1):
            cx = player_chunk_x + dx
            cz = player_chunk_z + dz
            if (cx, cz) not in loaded_chunks:
                blocks = generate_chunk(cx, cz)
                new_chunks[(cx, cz)] = blocks
    loaded_chunks.update(new_chunks)

# Unload chunks far away
def unload_chunks(player_chunk_x, player_chunk_z):
    global loaded_chunks
    keys_to_remove = []
    for (cx, cz) in loaded_chunks.keys():
        if abs(cx - player_chunk_x) > RENDER_DISTANCE or abs(cz - player_chunk_z) > RENDER_DISTANCE:
            for block in loaded_chunks[(cx, cz)]:
                destroy(block)
            keys_to_remove.append((cx, cz))
    for key in keys_to_remove:
        del loaded_chunks[key]

# Create player
player = FirstPersonController()
player.gravity = 0.5
player.speed = 5

# Handle block placement texture selection
def input(key):
    global current_texture
    if key == '1':
        current_texture = grass_texture
    if key == '2':
        current_texture = dirt_texture
    if key == '3':
        current_texture = stone_texture
    if key == '4':
        current_texture = wood_texture
    if key == '5':
        current_texture = leaves_texture
    print(f'Selected block: {current_texture.name}')

# Main update loop to load/unload chunks based on player position
def update():
    player_chunk_x = int(player.x // CHUNK_SIZE)
    player_chunk_z = int(player.z // CHUNK_SIZE)
    load_chunks(player_chunk_x, player_chunk_z)
    unload_chunks(player_chunk_x, player_chunk_z)

app.run()
