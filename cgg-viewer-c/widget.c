/*
 * widget.c
 *
 * a simple widget set based on SDL2 and LUA.
 *
 *  Created on: 2017-02-15
 *      Author: moose
 */
#include "widget.h"

struct {
    TWidget* w;
    
};


static 

static TWidget WIDGET_MOTHER;

int WidgetInit(void)
{

}


int WidgetQuit(void);
int IsWidget(void* w);
int WidgetCreate(TWidget* w, char* name, TCouple pos, TCouple size, TWidget* parent)
{
    return widget_create(w, name, pos, size, parent);
}

int is_widget(TWidget* w)
{
    if (NULL!= w)
    {
        // traversal widget instance list

        return 0;
    }
    return -1;
}

int widget_create(TWidget* w, char* name, TCouple pos, TCouple size, TWidget* parent)
{
    int r=-1;

    if (is_widget(w))
    {
        return r;  // widget already exist.
    }
    else
    {
        // set up name
        if ((strlen(name)>0) && (strlen(name)<=WIDGET_MAX_STRING_LENGTH))
        {
            strcat(w->name, name);
        }
        else
        {
            strcat(w->name, "Invalid Name");
        }
        // set up parent, or set to mother on case of invalid value.
        if (is_widget(parent))
        {
            w->parent = parent; 
        }
        else
        {
            w->parent = &WIDGET_MOTHER;
        }
        // set up pos and size
        w->pos.x = pos.x;
        w->pos.y = pos.y;
        w->size.width = size.width;
        w->size.height= size.height;

        if (NULL != ProviderCreate)
        {
            r = ProviderCreate(w, name, pos, size, parent);
        }

        return r;        
    }
    return -1;
}


#endif /* _WIDGET_H_ */
