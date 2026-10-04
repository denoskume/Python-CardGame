"""One geometry map for painting, pointer input and keyboard focus."""
import pygame


def compute_layout(size: tuple[int,int], state: str) -> dict[str, pygame.Rect]:
    w,h = size
    margin = max(16,min(48,w//28))
    width = min(w-2*margin,1040)
    left = (w-width)//2
    short = h < 500
    layout = {'content':pygame.Rect(left,78,width,h-94)}
    def button(name,x,y,bw,bh=48):
        layout['btn_'+name] = pygame.Rect(int(x),int(y),int(bw),int(bh))
    def bottom(names):
        gap=10
        bw=min(220,(width-gap*(len(names)-1))//len(names))
        start=(w-(bw*len(names)+gap*(len(names)-1)))//2
        for i,name in enumerate(names): button(name,start+i*(bw+gap),h-72,bw)
    if state=='START_SCREEN':
        # Keep the primary CTA in the hero area; secondary actions remain in the footer.
        if short:
            button('play',w//2-110,max(250,h-150),220)
        elif w>=850:
            hero_center = left + min(width//2, width//3)
            button('play',hero_center-110,300,220)
        else:
            button('play',w//2-110,min(h-150,380),220)
        gap=10
        bw=min(220,(width-gap)//2)
        start=(w-(bw*2+gap))//2
        button('help',start,h-72,bw)
        button('settings',start+bw+gap,h-72,bw)
    elif state=='MENU':
        field_w=min(420,width)
        y=170 if short else int(h*.32)
        layout['name_input']=pygame.Rect((w-field_w)//2,y,field_w,52)
        avatar_y=y+76
        for i in range(3): button('avatar_'+str(i),w//2-104+i*76,avatar_y,56,56)
        bottom(['back','continue'])
    elif state=='BET_SETUP':
        button('settings',w-margin-112,20,112,44)
        y=155 if short else int(h*.37)
        button('minus',w//2-130,y,48)
        button('plus',w//2+82,y,48)
        for i in range(3): button('turbo_'+str(i+1),w//2-118+i*82,y+64,72)
        bottom(['menu','start'])
    elif state=='SETTINGS':
        # Leave enough vertical clearance for the globally enlarged title/subtitle.
        y=140 if short else max(205,int(h*.34))
        gap=8; bw=min(180,(width-16)//3)
        for i,name in enumerate(['easy','normal','expert']):
            button(name,(w-(bw*3+gap*2))//2+i*(bw+gap),y,bw)
        button('sound',w//2-100,y+64,200)
        button('volume_down',w//2-118,y+124,48)
        button('volume_up',w//2+70,y+124,48)
        bottom(['back'])
    elif state=='HELP': bottom(['back'])
    elif state=='PAUSE': bottom(['resume'])
    elif state=='GAME_OVER': bottom(['menu','quit'])
    elif state=='RESULT': bottom(['menu','next','quit'])
    else: button('pause',w-margin-80,20,80,44)
    gap=max(12,min(44,width//24))
    card_h=min(258,int(h*(.25 if short else .34)))
    card_w=min(180,int(card_h*.70),(width-2*gap)//3)
    card_h=int(card_w/0.70)
    card_y=int(h*.42) if not short else 180
    card_y=min(card_y,h-100-card_h)
    start=(w-3*card_w-2*gap)//2
    for i in range(3):
        layout['card_'+str(i)]=pygame.Rect(start+i*(card_w+gap),card_y,card_w,card_h)
    return layout
