/*******************************************************************************
 *  cg-sdl.c
 *
 *  Author: Moose W. Oler
 *
 *  cg-widget is a Widget set for cgg-viewer(CrossGate Graphical Viewer). It is
 *  based on SDL2 and provides a LUA interface.
 *  
 ******************************************************************************/

#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#include <SDL2/SDL.h>
#include <SDL2/SDL_ttf.h>
#include <SDL2/SDL_image.h>

#include "cg-widget.h"

struct _ACGSDLInterface
{
    SDL_Window*     window;
    SDL_Renderer*   renderer;
    char            name[CG_WIDGET_MAX_STRING_LENGTH];
    CGCouple        pos;
    CGCouple        size;
    CGBool          quit;
    CGBool          draw;
    void            (*mainloop)(void* a);
};
typedef struct _ACGSDLInterface ACGSDLInterface;

static ACGSDLInterface sdl_interface;

void sdl_mainloop(void)
{
    SDL_Event e;
    while(sdl_interface.quit == CG_FALSE)
    {
        SDL_Delay(10);
        while (SDL_PollEvent(&e))
        {
            if (e.type == SDL_QUIT)
            {
                sdl_interface.quit=CG_TRUE;
            }
        }
        if (sdl_interface.draw == CG_TRUE)
        {
            SDL_RenderClear(sdl_interface.renderer);
            SDL_RenderPresent(sdl_interface.renderer);
            sdl_interface.draw = CG_FALSE;
        }
    }
}

int CGW_SDLInit(char* name, int width, int height)
{
	SDL_Window      *w;
	SDL_Renderer    *r;
    SDL_Rect        srect;

    // init SDL
	SDL_Init(SDL_INIT_EVERYTHING);

    // get screen resolution
    SDL_GetDisplayBounds(0, &srect);
    if ( width > srect.w || height > srect.h) 
    {
        SDL_Quit();
        return -1;
    }
    // create a centered window
    sdl_interface.pos.x = srect.w / 2 - width / 2;
    sdl_interface.pos.y = srect.h / 2 - height / 2;
    sdl_interface.size.w= width;
    sdl_interface.size.h= height;
    if ((NULL==name) || (strlen(name)==0))
    {
        strcpy(sdl_interface.name,"Untitled Window");
    }
    else
    {
        strcpy(sdl_interface.name, name);
    }
    w = SDL_CreateWindow(sdl_interface.name, 
                         sdl_interface.pos.x, sdl_interface.pos.y, 
                         sdl_interface.size.w,sdl_interface.size.h, 
                         SDL_WINDOW_SHOWN);
    if (NULL==w)
    {
        SDL_Quit();
        return -1;
    }
    else
    {
        sdl_interface.window = w;
    }

	r = SDL_CreateRenderer(sdl_interface.window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC);
    if (NULL==r)
    {
        SDL_Quit();
        return -1;
    }
    else
    {
        sdl_interface.renderer = r;
    }

    sdl_interface.quit = CG_FALSE;
    sdl_interface.draw = CG_TRUE;


	//IMG_Init(IMG_INIT_PNG);
	//TTF_Init();
	//SDL_StartTextInput();
    sdl_mainloop();
	return 0;
}

int CGW_SDLQuit(void)
{
    SDL_DestroyRenderer(sdl_interface.renderer);
    SDL_DestroyWindow(sdl_interface.window);
    SDL_Quit();
    return 0;
}
