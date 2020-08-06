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

union _TCouple {
    struct {
        int x;
        int y;
    };
    struct {
        int width;
        int height;
    };
};
typedef union _TCouple TCouple;

#endif /* _WIDGET_H_ */
