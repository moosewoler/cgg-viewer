/*******************************************************************************
 *  test.c
 *
 ******************************************************************************/

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cg/cg-widget.h"

/*******************************************************************************
 *      Testing Suit
 ******************************************************************************/
void test_cg_widget(void);
void test_cg_sdl(void);




int main(void)
{
    test_cg_sdl();
    test_cg_widget();
    return 0;
}

void test_cg_sdl(void)
{
    CGW_SDLInit(NULL, 600, 480);
    CGW_SDLQuit();
}

void test_cg_widget(void)
{
    CGWidget *w1, *w2, *w3;

    CGW_Init();

    w1 = CGW_WidgetCreate("oler", 0, 0, 10, 10);
    w2 = CGW_WidgetCreate("sxw", 10, 10, 100, 100);

    CGW_WidgetSetName(w1, "dundun");

    CGW_WidgetDestroy(w1);

    w3 = CGW_WidgetCreate("newoler", 0, 0, 10, 10);
    w1 = CGW_WidgetCreate("newdundun", 0,0, 120, 120);

    CGW_Quit();
}


/*******************************************************************************
 *      Testing code for kiss_sdl 
 ******************************************************************************/
//#include "lua.h"
//#include "lauxlib.h"
//#include "lualib.h"
//
//#include "kiss_sdl.h"

//int window_width, window_height;
//int textbox_width, textbox_height, window2_width, window2_height;
//int draw, quit;
//
//struct _label{
//    char text[128];
//    int x;
//    int y;
//}label;
//
//
//
//void error(lua_State* L, const char* fmt, ...)
//{
//    va_list argp;
//    va_start(argp, fmt);
//    vfprintf(stderr, fmt, argp);
//    va_end(argp);
//    lua_close(L);
//    exit(EXIT_FAILURE);
//}
//
//static void stackDump(lua_State* L)
//{
//    int i,j;
//    int top = lua_gettop(L);
//
//    printf("        ---stack top---\n");
//    for (i=-1;i>=-top;i--)
//    {
//        if (i == -1)
//        {
//            printf("-1 ---> ");
//            printf("| ");
//        }
//        else
//        {
//            printf("        | ");
//        }
//
//
//        int t=lua_type(L,i);
//        switch(t)
//        {
//            case LUA_TSTRING:
//                printf("%s", lua_tostring(L,i));
//                
//                if (strlen(lua_tostring(L,i))<=11)
//                {
//                    for (j=0; j<(11-strlen(lua_tostring(L,i))); j++)
//                        printf(" ");
//                }
//                break;
//
//            case LUA_TBOOLEAN:
//                if (lua_toboolean(L,i))
//                {
//                    printf("true       ");
//                }
//                else
//                {
//                    printf("false      ");
//                }
//                break;
//            case LUA_TNUMBER:
//                printf("%g", lua_tonumber(L,i));
//                for (j=0; j<(11-strlen(lua_tostring(L,i))); j++)
//                    printf(" ");
//                break;
//                break;
//            default:
//                printf("%s", lua_typename(L,t));
//                for (j=0; j<(11-strlen(lua_typename(L,t))); j++)
//                    printf(" ");
//                break;
//                break;
//        }
//        printf(" |\n");
//        printf("        ---------------\n");
//    }
//    printf("\n");
//}
//
//void read_config(lua_State* L, char* conf)
//{
//    if (luaL_loadfile(L, "config.lua") || (lua_pcall(L,0,0,0)))
//    {
//        error(L, "cannot run config file: %s", lua_tostring(L,-1));
//    }
//
//    stackDump(L);
//    lua_getglobal(L, "window_height");
//    stackDump(L);
//    window_height = (int)(lua_tonumber(L,-1));
//    stackDump(L);
//    lua_pop(L,1);
//    stackDump(L);
//
//    lua_getglobal(L, "window_width");
//    stackDump(L);
//    window_width = (int)(lua_tonumber(L,-1));
//    stackDump(L);
//    lua_pop(L,1);
//    stackDump(L);
//
//    printf("%d, %d\n", window_width, window_height);
//
//    // get label
//    lua_getglobal(L, "label");                     // -1 : button
//    stackDump(L);
//
//    if (!lua_istable(L,-1))
//        error(L, "'label' is not a table");
//    
//    lua_pushstring(L, "x");
//    stackDump(L);
//    lua_gettable(L,-2);
//    stackDump(L);
//    label.x = (int)(lua_tonumber(L,-1));
//    lua_pop(L,1);
//    stackDump(L);
//
//    lua_pushstring(L, "y");
//    stackDump(L);
//    lua_gettable(L,-2);
//    stackDump(L);
//    label.y = (int)(lua_tonumber(L,-1));
//    lua_pop(L,1);
//    stackDump(L);
//
//    lua_pushstring(L, "t");
//    stackDump(L);
//    lua_gettable(L,-2);                             
//    stackDump(L);
//    strcat(label.text, lua_tostring(L,-1));
//    lua_pop(L,1);
//    stackDump(L);
//    lua_pop(L,1);
//    stackDump(L);
//    
//    printf("%s, %d, %d\n", label.text, label.x, label.y);
//}
//
//
//int main(void)
//{
//
//    lua_State* L;
//
//	SDL_Renderer *renderer;
//	SDL_Event e;
//
//	kiss_array  objects, a1, a2; 
//	kiss_window window1;
//	kiss_label  label1 = {0};
//	kiss_entry  entry = {0};
//
//	quit = 0;
//	draw = 1;
//
//    L= luaL_newstate();
//    luaL_openlibs(L);
//    read_config(L, "config.lua");
//
//    // kiss_widget
//
//	renderer = kiss_init("kiss_sdl example 1", &objects, window_width, window_height);
//	if (!renderer) return 1;
//	kiss_array_new(&a1);
//	kiss_array_append(&objects, ARRAY_TYPE, &a1);
//	kiss_array_new(&a2);
//	kiss_array_append(&objects, ARRAY_TYPE, &a2);
//	kiss_window_new(&window1, NULL, 1, 0, 0, kiss_screen_width, kiss_screen_height);
//	kiss_label_new(&label1, &window1, label.text, label.x, label.y);
//
//    window1.visible = 1;
//    
//    while (!quit)
//    {
//		/* Some code may be written here */
//
//		SDL_Delay(10);
//		while (SDL_PollEvent(&e)) 
//        {
//			if (e.type == SDL_QUIT) quit = 1;
//
//			kiss_window_event(&window1, &e, &draw);
//        }
//		if (!draw) continue;
//
//        SDL_RenderClear(renderer);
//
//		kiss_window_draw(&window1, renderer);
//		kiss_label_draw(&label1, renderer);
//
//		SDL_RenderPresent(renderer);
//		draw = 0;
//    }
//
//	kiss_clean(&objects);
//
//    lua_close(L);
//
//    {
//        typedef enum 
//        {  
//            CG_UNKNOWN_TYPE = 0, 
//            CG_WINDOW_TYPE, 
//            CG_RENDERER_TYPE, 
//            CG_TEXTURE_TYPE, 
//            CG_SURFACE_TYPE,
//            CG_FONT_TYPE, 
//            CG_STRING_TYPE, 
//            CG_ARRAY_TYPE
//        } TCGType;
//
//        TCGType b=CG_STRING_TYPE;
//        printf("%d\n",b);
//    
//    }
//    return 0;
//}
