/*******************************************************************************
 *
 ******************************************************************************/

#ifndef _CG_WIDGET_H_
#define _CG_WIDGET_H_

/*******************************************************************************
 *      Types and Constants
 ******************************************************************************/

#define CG_WIDGET_MAX_COUNT         16
#define CG_WIDGET_MAX_STRING_LENGTH 256
#define CG_WIDGET_MAGIC_NUMBER      861007

typedef enum
{
    CG_FALSE = 0,
    CG_TRUE
} CGBool;

typedef enum 
{  
    CG_WIDGET_UNKNOWN = 0, 
    CG_WIDGET_LABEL,
    CG_WIDGET_PANEL
} CGType;

union _CGCouple 
{
    struct {
        int x;
        int y;
    };
    struct {
        int w;
        int h;
    };
};
typedef union _CGCouple CGCouple;

struct _CGWidget 
{
    // members
    char        name[CG_WIDGET_MAX_STRING_LENGTH];
    CGBool      visible;
    CGBool      focus;
    CGCouple    pos;
    CGCouple    size;
    //CGType      type;
    //int         ref;

    // functions
    void        (*create)(struct _CGWidget *w);
    void        (*destroy)(struct _CGWidget *w);
    void        (*draw)(struct _CGWidget *w);
    void        (*response)(struct _CGWidget *w);
};
typedef struct _CGWidget CGWidget;


//struct _CGFont
//{
//	TTF_Font   *font;
//    SDL_Color   color;
//	int         magic;
//	int         fontheight;
//	int         spacing;
//	int         lineheight;
//	int         advance;
//	int         ascent;
//};
//typedef struct _CGFont CGFont;

//struct _CGLabel
//{
//    CGWidget    widget;
//
//	char        text[CG_WIDGET_MAX_STRING_LENGTH];
//	CGFont      font;
//	CGWidget   *parent;
//};
//typedef struct _CGLabel CGLabel;


/* Length is number of elements, size is allocated size */
struct _TCGArray
{
	void **data;
	int *id;
	int length;
	int size;
	int ref;
};
typedef struct _TCGArray TCGArray;



#ifdef __cplusplus
extern "C" {
#endif

int         CGW_Init(void);
int         CGW_Quit(void);

CGWidget*   CGW_WidgetCreate(char* name, int x, int y, int w, int h);
void        CGW_WidgetDestroy(CGWidget* w);
int         CGW_WidgetSetName(CGWidget* w, char* name);

// cg-sdl
int         CGW_SDLInit(char* name, int w, int h);   
int         CGW_SDLQuit(void);

//int         CGW_WidgetSetPos();
//int         CGW_WidgetSetSize();
//int         CGW_WidgetSetVisible();
//int         CGW_WidgetSetFocus();


//CGLabel*    CGW_LabelNew(char* name, char* text, int x, int y, int w, int h);
//int         CGW_LabelSetFont(CGLabel* w, CGFont* font); 


#ifdef __cplusplus
}
#endif



#endif /* _CG_WIDGET_H_ */


/*******************************************************************************
 *      Aborted Code
 ******************************************************************************/

//#include <SDL2/SDL.h>
//#include <SDL2/SDL_ttf.h>
//#include <SDL2/SDL_image.h>

//#include <sys/types.h>
//#include <unistd.h>
//#include <dirent.h>

//#include <sys/stat.h>
//#include <string.h>
//#include <stdio.h>

//
//
//
//
//char *kiss_getcwd(char *buf, int size);
//int kiss_chdir(char *path);
//int kiss_getstat(char *pathname, kiss_stat *buf);
//kiss_dir *kiss_opendir(char *name);
//kiss_dirent *kiss_readdir(kiss_dir *dirp);
//int kiss_closedir(kiss_dir *dirp);
//int kiss_isdir(kiss_stat s);
//int kiss_isreg(kiss_stat s);
//int kiss_makerect(SDL_Rect *rect, int x, int y, int h, int w);
//int kiss_pointinrect(int x, int y, SDL_Rect *rect);
//int kiss_utf8next(char *str, int index);
//int kiss_utf8prev(char *str, int index);
//int kiss_utf8fix(char *str);
//char *kiss_string_copy(char *dest, size_t size, char *str1, char *str2);
//int kiss_string_compare(const void *a, const void *b);
//char *kiss_backspace(char *str);
//int kiss_array_new(kiss_array *a);
//void *kiss_array_data(kiss_array *a, int index);
//int kiss_array_id(kiss_array *a, int index);
//int kiss_array_assign(kiss_array *a, int index, int id, void *data);
//int kiss_array_append(kiss_array *a, int id, void *data);
//int kiss_array_appendstring(kiss_array *a, int id, char *text1, char *text2);
//int kiss_array_insert(kiss_array *a, int index, int id, void *data);
//int kiss_array_remove(kiss_array *a, int index);
//int kiss_array_free(kiss_array *a);
//unsigned int kiss_getticks(void);
//int kiss_maxlength(kiss_font font, int width, char *str1, char *str2);
//int kiss_textwidth(kiss_font font, char *str1, char *str2);
//int kiss_renderimage(SDL_Renderer *renderer, kiss_image image,
//	int x, int y, SDL_Rect *clip);
//int kiss_rendertext(SDL_Renderer *renderer, char *text, int x, int y,
//	kiss_font font, SDL_Color color);
//int kiss_fillrect(SDL_Renderer *renderer, SDL_Rect *rect, SDL_Color color);
//int kiss_decorate(SDL_Renderer *renderer, SDL_Rect *rect, SDL_Color color,
//	int edge);
//int kiss_image_new(kiss_image *image, char *fname, kiss_array *a,
//	SDL_Renderer* renderer);
//int kiss_font_new(kiss_font *font, char *fname, kiss_array *a, int size);
//SDL_Renderer* kiss_init(char* title, kiss_array *a, int w, int h);
//int kiss_clean(kiss_array *a);
//int kiss_window_new(kiss_window *window, kiss_window *wdw, int decorate,
//	int x, int y, int w, int h);
//int kiss_window_event(kiss_window *window, SDL_Event *event, int *draw);
//int kiss_window_draw(kiss_window *window, SDL_Renderer *renderer);
//int kiss_label_new(kiss_label *label, kiss_window *wdw, char *text,
//	int x, int y);
//int kiss_label_draw(kiss_label *label, SDL_Renderer *renderer);
//int kiss_button_new(kiss_button *button, kiss_window *wdw, char *text,
//	int x, int y);
//int kiss_button_event(kiss_button *button, SDL_Event *event, int *draw);
//int kiss_button_draw(kiss_button *button, SDL_Renderer *renderer);
//int kiss_selectbutton_new(kiss_selectbutton *selectbutton, kiss_window *wdw,
//	int x, int y);
//int kiss_selectbutton_event(kiss_selectbutton *selectbutton,
//	SDL_Event *event, int *draw);
//int kiss_selectbutton_draw(kiss_selectbutton *selectbutton,
//	SDL_Renderer *renderer);
//int kiss_vscrollbar_new(kiss_vscrollbar *vscrollbar, kiss_window *wdw,
//	int x, int y, int h);
//int kiss_vscrollbar_event(kiss_vscrollbar *vscrollbar, SDL_Event *event,
//	int *draw);
//int kiss_vscrollbar_draw(kiss_vscrollbar *vscrollbar,
//	SDL_Renderer *renderer);
//int kiss_hscrollbar_new(kiss_hscrollbar *hscrollbar, kiss_window *wdw,
//	int x, int y, int w);
//int kiss_hscrollbar_event(kiss_hscrollbar *hscrollbar, SDL_Event *event,
//	int *draw);
//int kiss_hscrollbar_draw(kiss_hscrollbar *hscrollbar,
//	SDL_Renderer *renderer);
//int kiss_progressbar_new(kiss_progressbar *progressbar, kiss_window *wdw,
//	int x, int y, int w);
//int kiss_progressbar_event(kiss_progressbar *progressbar, SDL_Event *event,
//	int *draw);
//int kiss_progressbar_draw(kiss_progressbar *progressbar,
//	SDL_Renderer *renderer);
//int kiss_entry_new(kiss_entry *entry, kiss_window *wdw, int decorate,
//	char *text, int x, int y, int w);
//int kiss_entry_event(kiss_entry *entry, SDL_Event *event, int *draw);
//int kiss_entry_draw(kiss_entry *entry, SDL_Renderer *renderer);
//int kiss_textbox_new(kiss_textbox *textbox, kiss_window *wdw, int decorate,
//	kiss_array *a, int x, int y, int w, int h);
//int kiss_textbox_event(kiss_textbox *textbox, SDL_Event *event, int *draw);
//int kiss_textbox_draw(kiss_textbox *textbox, SDL_Renderer *renderer);
//int kiss_combobox_new(kiss_combobox *combobox, kiss_window *wdw,
//	char *text, kiss_array *a, int x, int y, int w, int h);
//int kiss_combobox_event(kiss_combobox *combobox, SDL_Event *event,
//	int *draw);
//int kiss_combobox_draw(kiss_combobox *combobox, SDL_Renderer *renderer);
//
//
//
//
//typedef struct kiss_image {
//	SDL_Texture *image;
//	int magic;
//	int w;
//	int h;
//} kiss_image;
//
//
//typedef struct kiss_button {
//	int visible;
//	int focus;
//	SDL_Rect rect;
//	int textx;
//	int texty;
//	char text[KISS_MAX_LENGTH];
//	int active;
//	int prelight;
//	SDL_Color textcolor;
//	kiss_font font;
//	kiss_image normalimg;
//	kiss_image activeimg;
//	kiss_image prelightimg;
//	kiss_window *wdw;
//} kiss_button;
//
//typedef struct kiss_selectbutton {
//	int visible;
//	int focus;
//	SDL_Rect rect;
//	int selected;
//	kiss_image selectedimg;
//	kiss_image unselectedimg;
//	kiss_window *wdw;
//} kiss_selectbutton;
//
//typedef struct kiss_vscrollbar {
//	int visible;
//	int focus;
//	SDL_Rect uprect;
//	SDL_Rect downrect;
//	SDL_Rect sliderrect;
//	int maxpos;
//	double fraction;
//	double step;
//	unsigned int lasttick;
//	int downclicked;
//	int upclicked;
//	int sliderclicked;
//	kiss_image up;
//	kiss_image down;
//	kiss_image vslider;
//	kiss_window *wdw;
//} kiss_vscrollbar;
//
//typedef struct kiss_hscrollbar {
//	int visible;
//	int focus;
//	SDL_Rect leftrect;
//	SDL_Rect rightrect;
//	SDL_Rect sliderrect;
//	int maxpos;
//	double fraction;
//	double step;
//	unsigned int lasttick;
//	int leftclicked;
//	int rightclicked;
//	int sliderclicked;
//	kiss_image left;
//	kiss_image right;
//	kiss_image hslider;
//	kiss_window *wdw;
//} kiss_hscrollbar;
//
//typedef struct kiss_progressbar {
//	int visible;
//	SDL_Rect rect;
//	SDL_Rect barrect;
//	int width;
//	double fraction;
//	double step;
//	SDL_Color bg;
//	unsigned int lasttick;
//	int run;
//	kiss_image bar;
//	kiss_window *wdw;
//} kiss_progressbar;
//
//typedef struct kiss_entry {
//	int visible;
//	int focus;
//	SDL_Rect rect;
//	int decorate;
//	int textx;
//	int texty;
//	char text[KISS_MAX_LENGTH];
//	int active;
//	int textwidth;
//	int selection[4];
//	int cursor[2];
//	SDL_Color normalcolor;
//	SDL_Color activecolor;
//	SDL_Color bg;
//	kiss_font font;
//	kiss_window *wdw;
//} kiss_entry;
//
//typedef struct kiss_textbox {
//	int visible;
//	int focus;
//	SDL_Rect rect;
//	int decorate;
//	kiss_array *array;
//	SDL_Rect textrect;
//	int firstline;
//	int maxlines;
//	int textwidth;
//	int highlightline;
//	int selectedline;
//	int selection[4];
//	int cursor[2];
//	SDL_Color textcolor;
//	SDL_Color hlcolor;
//	SDL_Color bg;
//	kiss_font font;
//	kiss_window *wdw;
//} kiss_textbox;
//
//typedef struct kiss_combobox {
//	int visible;
//	char text[KISS_MAX_LENGTH];
//	kiss_entry entry;
//	kiss_window window;
//	kiss_vscrollbar vscrollbar;
//	kiss_textbox textbox;
//	kiss_image combo;
//	kiss_window *wdw;
//} kiss_combobox;

//extern SDL_Color kiss_white, kiss_black, kiss_green, kiss_blue,
//		kiss_lightblue;
//extern kiss_font kiss_textfont, kiss_buttonfont;
//extern kiss_image kiss_normal, kiss_prelight, kiss_active, kiss_bar,
//	kiss_up, kiss_down, kiss_left, kiss_right, kiss_vslider,
//	kiss_hslider, kiss_selected, kiss_unselected, kiss_combo;
//extern double kiss_spacing;
//extern int kiss_textfont_size, kiss_buttonfont_size;
//extern int kiss_click_interval, kiss_progress_interval;
//extern int kiss_slider_padding;
//extern int kiss_border, kiss_edge;
//extern int kiss_screen_width, kiss_screen_height;
