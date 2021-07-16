import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
import pyrr
from ObjLoader import ObjLoader


vertex_shader = """
# version 330

layout(location = 0) in vec3 in_position;
layout(location = 1) in vec3 in_texture;
layout(location = 2) in vec3 in_normal;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

out vec3 Normal;
out vec3 fragPos;

void main()
{   
    gl_Position = projection * view * model * vec4(in_position, 1.0f);
    fragPos = vec3(model * vec4(in_position, 1.0f));
    Normal = mat3(transpose(inverse(model))) * in_normal;
}
"""

fragment_shader = """
# version 330

struct Material {
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    float shininess;
}; 
  
uniform Material material;

struct Light {
    vec3 position;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
};

uniform Light light;  

in vec3 Normal;
in vec3 fragPos;  
out vec4 fragColor; 

uniform vec3 viewPos;

void main()
{   
    
    // ambient
    vec3 ambient = light.ambient * material.ambient;
    
    // diffuse 
    vec3 norm = normalize(Normal);
    vec3 lightDir = normalize(light.position - fragPos);
    float diff = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = light.diffuse * (diff * material.diffuse);
    
    // specular
    vec3 viewDir = normalize(viewPos - fragPos);
    vec3 reflectDir = reflect(-lightDir, norm);  
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
    vec3 specular = light.specular * (spec * material.specular);  
    
    // fragment output
    vec3 result = ambient + diffuse + specular;
    fragColor = vec4(result, 1.0);
     
}
"""

vertex_shader_light = """
# version 330

layout(location = 0) in vec3 position;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

void main()
{   
    gl_Position = projection * view * model * vec4(position, 1.0f);
}
"""

fragment_shader_light = """
# version 330

out vec4 fragColor; 

void main()
{   
    fragColor = vec4(0.8f, 0.8f, 0.8f, 1.0f);
}
"""


def initialize():

    if not glfw.init():
        raise Exception("glfw can not be initialized!")

    display = (1280, 720)  # 1280, 720
    window = glfw.create_window(display[0], display[1], "OpenGL window", None, None)

    if not window:
        glfw.terminate()
        raise Exception("glfw window can not be created!")

    # glfw.window_hint(glfw.SAMPLES, 4)
    glfw.make_context_current(window)

    # DATA SETUP

    vertex_data, indices = ObjLoader.load_model("obj/x.obj")
    light_data, light_indices = ObjLoader.load_model("obj/light_bulb.obj")

    # VERTEX SETUP LOGIC

    vao = glGenVertexArrays(3)
    vbo = glGenBuffers(3)
    ebo = glGenBuffers(3)

    # MAIN OBJECT

    glBindVertexArray(vao[0])

    glBindBuffer(GL_ARRAY_BUFFER, vbo[0])
    glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo[0])
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)  # positions
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, vertex_data.itemsize * 8, ctypes.c_void_p(0))

    # glEnableVertexAttribArray(1)  # textures - NONE
    # glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, vertex_data.itemsize * 8, ctypes.c_void_p(12))

    glEnableVertexAttribArray(2)  # normals
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, vertex_data.itemsize * 8, ctypes.c_void_p(20))

    glBindVertexArray(0)

    # LIGHT BULB

    glBindVertexArray(vao[1])

    glBindBuffer(GL_ARRAY_BUFFER, vbo[1])
    glBufferData(GL_ARRAY_BUFFER, light_data.nbytes, light_data, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo[1])
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, light_indices.nbytes, light_indices, GL_STATIC_DRAW)

    glEnableVertexAttribArray(0)  # positions
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, light_data.itemsize * 8, ctypes.c_void_p(0))

    # glEnableVertexAttribArray(1)  # textures - NONE
    # glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, light_data.itemsize * 8, ctypes.c_void_p(12))

    glEnableVertexAttribArray(2)  # normals
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, light_data.itemsize * 8, ctypes.c_void_p(20))

    glBindVertexArray(0)

    # COMMON MATRICES & VECTORS

    projection = pyrr.matrix44.create_perspective_projection_matrix(45, (display[0] / display[1]), 0.1, 400)
    view = pyrr.matrix44.create_look_at([0.0, 10.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 1.0])
    light_position = [0, 0, 0]

    # OBJECT SHADER

    shader = compileProgram(compileShader(vertex_shader, GL_VERTEX_SHADER),
                            compileShader(fragment_shader, GL_FRAGMENT_SHADER))

    projection_loc = glGetUniformLocation(shader, "projection")
    view_loc = glGetUniformLocation(shader, "view")
    model_loc = glGetUniformLocation(shader, "model")

    material_ambient_loc = glGetUniformLocation(shader, "material.ambient")
    material_diffuse_loc = glGetUniformLocation(shader, "material.diffuse")
    material_specular_loc = glGetUniformLocation(shader, "material.specular")
    material_shininess_loc = glGetUniformLocation(shader, "material.shininess")

    light_position_loc = glGetUniformLocation(shader, "light.position")
    light_ambient_loc = glGetUniformLocation(shader, "light.ambient")
    light_diffuse_loc = glGetUniformLocation(shader, "light.diffuse")
    light_specular_loc = glGetUniformLocation(shader, "light.specular")

    view_position_loc = glGetUniformLocation(shader, "viewPos")

    glUseProgram(shader)

    # UNIFORMS

    glUniform3f(material_ambient_loc, 0.1, 0.4, 0.3)
    glUniform3f(material_diffuse_loc, 0.5, 0.6, 0.7)
    glUniform3f(material_specular_loc, 0.04, 0.04, 0.04)
    glUniform1f(material_shininess_loc, 128.0 * .08)

    glUniform3fv(light_position_loc, 1, light_position)
    glUniform3f(light_ambient_loc, 0.8, 0.7, 0.9)
    glUniform3f(light_diffuse_loc, 0.6, 0.6, 0.6)
    glUniform3f(light_specular_loc, 1.0, 1.0, 1.0)

    glUniform3f(view_position_loc, 0.0, 100.0, 0.0)

    # LIGHT SHADER

    light_shader = compileProgram(compileShader(vertex_shader_light, GL_VERTEX_SHADER),
                                  compileShader(fragment_shader_light, GL_FRAGMENT_SHADER))

    projection_loc_light = glGetUniformLocation(light_shader, "projection")
    view_loc_light = glGetUniformLocation(light_shader, "view")
    model_loc_light = glGetUniformLocation(light_shader, "model")

    glUseProgram(light_shader)

    # GL SETUP

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_MULTISAMPLE)
    glClearColor(0.7, 0.7, 0.8, 1.0)
    n = 2.63

    # MAIN APP LOOP

    while not glfw.window_should_close(window):

        glfw.swap_buffers(window)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        step = 0.24 * glfw.get_time()

        # COMPUTE MAIN OBJECT

        glUseProgram(shader)

        glUniformMatrix4fv(projection_loc, 1, GL_FALSE, projection)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)

        rot_x = pyrr.Matrix44.from_x_rotation(step * 2 * n)
        rot_y = pyrr.Matrix44.from_y_rotation(step * 6 * n)
        rot_z = pyrr.Matrix44.from_z_rotation(step * n)
        object_model = rot_z * rot_y * rot_x

        glUniformMatrix4fv(model_loc, 1, GL_FALSE, object_model)

        glBindVertexArray(vao[0])
        glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

        # COMPUTE MAIN OBJECT'S LIGHT

        light_x = -4
        light_y = 5
        light_z = 4

        glUniformMatrix4fv(projection_loc, 1, GL_FALSE, projection)
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
        glUniform3f(light_position_loc, light_x, light_y, light_z)

        # COMPUTE LIGHT BULB OBJECT

        glUseProgram(light_shader)

        glUniformMatrix4fv(projection_loc_light, 1, GL_FALSE, projection)
        glUniformMatrix4fv(view_loc_light, 1, GL_FALSE, view)

        translate = pyrr.matrix44.create_from_translation([light_x, light_y, light_z])
        scale = pyrr.matrix44.create_from_scale([1/4, 1/4, 1/4])
        light_model = scale + translate

        glUniformMatrix4fv(model_loc_light, 1, GL_FALSE, light_model)

        glBindVertexArray(vao[1])
        glDrawElements(GL_TRIANGLES, len(light_indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

        glfw.poll_events()

    glDeleteProgram(shader)
    glDeleteProgram(light_shader)
    glfw.terminate()


initialize()
