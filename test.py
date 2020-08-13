import pygame_lib
import nn_lib
import node_vis
import pygame as pg

def test_e_boxes():
    screen,clock = pygame_lib.init_pygame((1000,1000))
    #params["font_size"], params["color_active"], params["color_inactive"], params["min_width"], params["text_color"]
    all_text_boxes = pygame_lib.text_boxes()
    all_text_boxes.add_box((100,100), 2 ,font_size = 50)
    all_text_boxes.add_box((100,200), 2 ,text_color = pg.Color("red"))
    all_text_boxes.add_box((100,300), 2, text_c = {"active" : pg.Color("blue"), "inactive" : pg.Color("red")})
    all_text_boxes.add_box((100,400) ,3, color_inactive = pg.Color("purple"))
    all_text_boxes.add_box((100,500) ,5, min_width = 50)
    all_text_boxes.add_box((100,600) ,7 ,font_size = 25, text_color = pg.Color("orange"), color_active = pg.Color("red"), color_inactive = pg.Color("grey"), min_width = 500)
    all_text_boxes.add_box((100,700) ,9)
    all_text_boxes.add_box((500,100) ,11)
    all_text_boxes.add_box((500,200) ,11, interact = False)

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