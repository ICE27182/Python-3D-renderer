<!-- 
## How to render?
### What features should my renderer possess?
- Workability
- Able to read .obj file
- Support parallel light
- Z-buffer
- Rasterization
### What other features does my renderer possess?
- Able to manipulate models to some extent
### What features can be added?
- UV Texture
- Normal Map
- Smooth Shading
- Point Light Source
- Anti-aliasing (FXAA) 
-->
## Objectives
1. Modes:
        - solid
        - depth
        - lines
        - normal
2. Parallel & Point Light Sources
3. Support for Texture & Normal Map
4. Support for Smooth Shading
5. Support for Shadows
6. Camera Control
7. Support for screen-shot
8. Support for high-resolution, offline, statistic rendering

## Coding
## Rendering Procedure
- Read .obj (and .mtl) file(s)  
--- Enter rendering procedure ---
- initiate depth-buffer
- **for over all objects**
    - **for over all faces (triangles) in each object**
        - substract 3 vertices by the camera coordinate
        - rotate the 3 vertices
        - cull the face if needed
        - clip the triangle against the near z-plane and get 0/1/2 triangles
        - retrieve the svn (if smooth shading) or u&v (if textured) or nu&nv (if normal_mapped)  
--- Start to Rasterize ---  
        - **len(inside) = 3**
            - sort three vertices  
            - cull some vertices
            - **if solid**
                - **if smooth_shading**
                    - rasterize (get x3d, y3d, z3d, snx, sny, snz)
                        - calculate luminace
                - **if flat_shading**
                    - rasterize (get x3d, y3d, z3d, nx, ny, nz)
                        - calculate luminace
            - **if textured & normal_mapped**  
                => flat_shading  
                - rasterize (get x3d, y3d, z3d, u, v, color, normal)
                    - calculate luminance
            - **if textured**
                - **if smooth_shading**
                    - rasterize (get x3d, y3d, z3d, u, v, color, snx, sny, snz)
                        - calculate luminace
                - **if flat_shading**
                    - rasterize (get x3d, y3d, z3d, u, v, color, nx, ny, nz)
                        - calculate luminace  
            - **if normal_mapped**  
                => flat_shading
                - rasterize (get x3d, y3d, z3d, u, v, nx, ny, nz)
                    - calculate luminace  

### In terms of performance, list is the best representing coordinates
Use Build-in List  
![Tuple > List > Dictionary > Class > array.array <=> collections.deque](Data_type_test_outcome.png)


## Data
### Object
#### Public
- objects               [Object, Object, ...]
- default_loading_dir   "E:\\Programming\\Python\\Python-3D-renderer\\models\\"
- default_uv_map_size   (INTp, R, G, B)
### Private
- name                  str
- shade_smooth          bool
- mtl                   Material/None
- hastexture            bool
- hasnormal_map         bool
- culling               bool
- v                     [[x, y, z], [...], ...]
- vt                    [(u, v), (...), ...]
- vn                    [[x, y, z], [...], ...]
- faces                 [[(A_index:INTw, B_index:INTw, C_index:INTw), 
                          (Auv_index:INTw, Buv_index:INTw, Cuv_index:INTw)/None, 
                          normal_index:INTw/None,
                          (Asn_index:INTw, Bsn_index:INTw, Csn_index:INTw)/None],
                         [...],
                         ...]
- rotation              ((float, float, float), (..., ..., ...), (...))
- hidden                bool
- static                bool
- shadow                bool
- svn                   [[x, y, z], [...], ...]


### Material
#### Public
- materials             {name:Png, ...:..., ...}
#### Private
- name                  str
<!-- - texture               None/Png -->
- normal_map            None/Png
- texture               None/Png
- texture_path          None/str
- normal_map_path       None/str

### Transformation (Object)
#### public
- transformations       {trans_name:Transformation, ...:..., ...}
#### Private
- center                [x, y, z]
- x_r                   float                         
- y_r                   float                         
- z_r                   float    
- mtl                   Material/None                     




### Light
#### Public
- light_sources         {name:Light}
#### Private
<!-- - strength              (NUM, NUM, NUM)
- position              (x, y, z)  
- direction             None/(x, y, z)
- cam_space_position    (x, y, z) -->
- name                  str/None
- x                     float
- y                     float
- z                     float
- dirx                  float
- diry                  float
- dirz                  float
- r                     INT[0, 255]
- g                     INT[0, 255]
- b                     INT[0, 255]
- x_in_cam              float
- y_in_cam              float
- z_in_cam              float
- dirx_in_cam           float
- diry_in_cam           float
- dirz_in_cam           float
- type                  0/1/2
- hidden                bool
- shadow                bool
- shadow_map0           [[z, z, ...], [...], ...]/None
- shadow_map1           [[z, z, ...], [...], ...]/None
- shadow_map2           [[z, z, ...], [...], ...]/None
- shadow_map3           [[z, z, ...], [...], ...]/None
- shadow_map4           [[z, z, ...], [...], ...]/None
- shadow_map5           [[z, z, ...], [...], ...]/None
- shadow_map6           [[z, z, ...], [...], ...]/None
- rotation0             ((float, float, float), (..., ..., ...), (...))
- rotation1             ((float, float, float), (..., ..., ...), (...))
- rotation2             ((float, float, float), (..., ..., ...), (...))
- rotation3             ((float, float, float), (..., ..., ...), (...))
- rotation4             ((float, float, float), (..., ..., ...), (...))
- rotation5             ((float, float, float), (..., ..., ...), (...))
- rotation6             ((float, float, float), (..., ..., ...), (...))
- z_near                float
- z_far                 float


### Camera
#### Private
- x                     float
- y                     float
- z                     float
- yaw                   float
- pitch                 float
- roll                  float
- z_near                float
- z_far                 float
- fov                   NUM(0, 180)
<!-- - fov_scalar            NUM(0, +inf) -->
- width                 INTp
- height                INTp
- fxaa                  bool
- obj_buffer            bool
- rendering_plane_z     float
- rotation              [[Xx, Xy, Xz],
                         [Yx, Yy, Yz],
                         [Zx, Zy, Zz]]
- light                 Light/None



### Scene
#### Private




### render
- frame                 [[(R:INT[0, 255], G:INT[0, 255], B:[0, 255]), (...), ...],
                         [...],
                         ...]
- depth_buffer          [[(z, u, v, obj), (...), ...],
                         [...],
                         ...]




```
if bake:
    for light in lights:
        if type == 0:
            light_render()
        else:
            light_render


```


# ICE
Load obj(file) - load mtl - initiate transform