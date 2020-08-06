/*
 * widget.h
 *
 * a simple widget set based on SDL2 and LUA.
 *
 *  Created on: 2017-02-15
 *      Author: moose
 */

#ifndef _WIDGET_H_
#define _WIDGET_H_

#define WIDGET_MAX_STRING_LENGTH 128

union _TCouple 
{
    struct {
        int x;
        int y;
    };
    struct {
        int width;
        int height;
    }
};
typedef union _TCouple TCouple;

typedef int (*TCallback)(void* o);

struct _TWidget 
{
    char    name[WIDGET_MAX_STRING_LENGTH];
    TCouple pos;
    TCouple size;
    struct _TWidget* parent;

    //TCallback   OnCreate;
    //TCallback   OnDestroy;
   
    int (*ProviderCreate)(struct _TWidget* w, char* name, TCouple pos, TCouple size, struct _TWidget* parent);
    int (*ProviderDestroy)(struct _TWidget* w);
    int (*ProviderChangeName)(struct _TWidget* w, char* name);
    int (*ProviderChangePosition)(struct _TWidget* w, TCouple pos);
    int (*ProviderChangeSize)(struct _TWidget* w, TCouple pos);
};

typedef struct _TWidget TWidget;

int WidgetInit(void);
int WidgetQuit(void);
int IsWidget(void* w);
TWidget* WidgetCreate(char* name, TCouple pos, TCouple size, TWidget* parent);

#endif /* _WIDGET_H_ */
