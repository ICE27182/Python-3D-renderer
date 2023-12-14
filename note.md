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
## How to write my code?
### object attributes
- v
- vt
- vn
- f
- filepath
- id
---
- smooth_shading
- textured
- normal_mapped
## Rendering Procedure
- Read .obj (and .mtl) file(s)  
--- Enter rendering procedure ---
- initiate z-buffer
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
                - rasterize (get x3d, y3d, z3d, u, v, color, nx, ny, nz)
                    - calculate luminace  

### In terms of performance, list is the best representing coordinates
Use Build-in List  
![Tuple > List > Dictionary > Class > array.array <=> collections.deque](Data_type_test_outcome.png)

