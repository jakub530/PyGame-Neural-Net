import pygame_lib
import nn_lib
import node_vis
import pygame as pg

def test_e_boxes():
    screen,clock = pygame_lib.init_pygame((1000,1000))
    #params["font_size"], params["color_active"], params["color_inactive"], params["min_width"], params["text_color"]
    all_text_boxes = pygame_lib.text_boxes(text_c = {"active" : pg.Color("LAVENDER"), "inactive" : pg.Color("KHAKI")})
    all_text_boxes.add_box((500,50), 2 ,font_size = 50, text = "Font Size 50 Test")
    all_text_boxes.add_box((500,100), 2 ,use_frame = False, text = "No frame Test")
    all_text_boxes.add_box((500,200) ,11, interact = False, text = "No interact Test")
    all_text_boxes.add_box((500,300) ,11, use_gradient = False, text = "No gradient Test")
    all_text_boxes.add_box((500,400) ,11, use_background = False, text = "No background Test")
    all_text_boxes.add_box((500,500) ,11, match_size = True, text = "Match Test")
    all_text_boxes.add_box((500,700) ,11, fixed_width = True, size = [90,90], text = "Fixed size test")
    all_text_boxes.add_box((500,800) ,11, min_width = 300, text = "Min width 300 test")

    all_text_boxes.add_box((100,100), 2, text_c = {"active" : pg.Color("blue"), "inactive" : pg.Color("red")}, text = "Text color test")
    all_text_boxes.add_box((100,200), 2, background_c = {"active" : pg.Color("maroon"), "inactive" : pg.Color("goldenrod")}, text = "Background color test")
    all_text_boxes.add_box((100,300), 2, frame_c = {"active" : pg.Color("MEDIUMSLATEBLUE"), "inactive" : pg.Color("AQUAMARINE")}, text = "Frame color test")
    all_text_boxes.add_box((100,400) ,3, gradient_c = {"active" : pg.Color("GREENYELLOW"), "inactive" : pg.Color("MAGENTA")}, text = "Gradient color test")

    done = False

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            if event.type == pg.KEYDOWN:
                if event.key==pg.K_ESCAPE:
                    done = True

            all_text_boxes.check_events(event)

        screen.fill((30, 30, 30))
        all_text_boxes.display_boxes(screen)
        pg.display.flip()
        clock.tick(30)

if __name__ == '__main__':
    pg.init()
    test_e_boxes()
    pg.quit()