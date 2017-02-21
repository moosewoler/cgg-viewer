/*******************************************************************************
 *  cg-widget.c
 *
 *  Author: Moose W. Oler
 *
 *  cg-widget is a Widget set for cgg-viewer(CrossGate Graphical Viewer). It is
 *  based on SDL2 and provides a LUA interface.
 *
 *  
 ******************************************************************************/

#include <string.h>
#include <stdio.h>
#include <stdlib.h>

#include "cg-widget.h"

struct _ACGWidget
{
    CGWidget    *w;
    CGType      type;
    int         ref;
};
typedef struct _ACGWidget ACGWidget;

static ACGWidget container[CG_WIDGET_MAX_COUNT];

/*******************************************************************************
 *      Local Functions
 ******************************************************************************/
void widget_infoall(char* fname);



int CGW_Init(void)
{
    int i;
    for (i=0;i<CG_WIDGET_MAX_COUNT;i++)
    {
        container[i].w = NULL;
        container[i].type = CG_WIDGET_UNKNOWN;
        container[i].ref = 0;
    }

    widget_infoall("CGW_Init");

    return 0;
}

int CGW_Quit(void)
{
    int i;

    widget_infoall("CGW_Quit");
    for (i=0;i<CG_WIDGET_MAX_COUNT;i++)
    {
        if (NULL!=container[i].w)
        {
            CGWidget *w = container[i].w;
            CGW_WidgetDestroy(w);
        }
    }

    widget_infoall("CGW_Quit All Destroyed.");

    return 0;
}

CGWidget* CGW_WidgetCreate(char* name, int x, int y, int width, int height)
{
    int i;

    for (i=0;i<CG_WIDGET_MAX_COUNT;i++)
    {
        if (NULL==container[i].w)
        {
            CGWidget* w;

            w=(CGWidget*)malloc(sizeof(CGWidget));

            if (NULL == w)
            {
                return w;
            }
            else
            {
                container[i].w=w;
                container[i].type=CG_WIDGET_UNKNOWN;
                container[i].ref=1;

                CGW_WidgetSetName(w, name);
                w->visible = CG_FALSE;
                w->focus   = CG_FALSE;
                w->pos.x   = x;
                w->pos.y   = y;
                w->size.w  = width;
                w->size.h  = height;
                w->create  = NULL;
                w->destroy = NULL;
                w->draw    = NULL;
                w->response= NULL;

                break;
            }
        }
    }

    widget_infoall("WidgetCreate");

    // return a CGWidget
    if (i>=CG_WIDGET_MAX_COUNT)
    {
        return NULL;
    }
    else
    {
        return container[i].w;
    }
}

void CGW_WidgetDestroy(CGWidget* w)
{
    int i;

    for (i=0;i<CG_WIDGET_MAX_COUNT;i++)
    {
        if (w == container[i].w)
        {
            free(w);
            container[i].w = NULL;
            container[i].type = CG_WIDGET_UNKNOWN;
            container[i].ref = 0;
         }
    }

    widget_infoall("WidgetDestroy");
}

 

int CGW_WidgetSetName(CGWidget* w, char* name)
{
    if (strlen(name) < CG_WIDGET_MAX_STRING_LENGTH)
    {
        strcpy(w->name, name);
        return 0;
    }

    {
        return -1;
    }
}


void widget_infoall(char* fname)
{
    int i;

    printf("\n");
    printf("----- List all registered widgets @ %s ------------\n", fname);
    for (i=0;i<CG_WIDGET_MAX_COUNT;i++)
    {
        if (NULL!=container[i].w)
        {
            printf("w[%d] = ", i);
            switch (container[i].type)
            {
                case CG_WIDGET_LABEL: 
                    printf("LABEL named: %s pos={%d, %d}, size={%d, %d}\n", container[i].w->name, container[i].w->pos.x, container[i].w->pos.y, container[i].w->size.w, container[i].w->size.h);
                    break;
                case CG_WIDGET_UNKNOWN:
                    printf("UNKNOWN named: %s pos={%d, %d}, size={%d, %d}\n", container[i].w->name, container[i].w->pos.x, container[i].w->pos.y, container[i].w->size.w, container[i].w->size.h);
                    break;
                default:
                    printf("INVALID!\n");
            }
        }
    }
    printf("------------------------------------------------------------\n\n");
}
