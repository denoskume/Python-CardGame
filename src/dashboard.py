"""Read-only rendering: the controller owns state and all interactive geometry."""
import math
import pygame
from theme import BG,PANEL,LINE,TEXT,MUTED,RED,GREEN,GOLD
from game_statistics import summarize_rounds
from history_table import aggregate_players


def text(screen,fonts,value,pos,kind='body',color=TEXT,center=False,max_width=None):
    font=fonts[kind]
    value=str(value)
    if max_width:
        while value and font.size(value)[0]>max_width:
            value=value[:-2]+'…' if len(value)>2 else ''
    surface=font.render(value,True,color)
    rect=surface.get_rect(center=pos) if center else surface.get_rect(topleft=pos)
    screen.blit(surface,rect)
    return rect


def wrapped(screen,fonts,value,x,y,width,kind='body',color=MUTED):
    words=value.split(); line=''
    for word in words:
        candidate=(line+' '+word).strip()
        if fonts[kind].size(candidate)[0]>width and line:
            text(screen,fonts,line,(x,y),kind,color)
            y+=fonts[kind].get_linesize()+5
            line=word
        else: line=candidate
    if line:
        text(screen,fonts,line,(x,y),kind,color)
        y+=fonts[kind].get_linesize()+5
    return y


def panel(screen,rect):
    pygame.draw.rect(screen,PANEL,rect,border_radius=18)
    pygame.draw.rect(screen,LINE,rect,1,border_radius=18)


def card(screen,fonts,rect,revealed=False,is_red=False,selected=False):
    shadow=rect.move(0,7)
    pygame.draw.rect(screen,(6,9,13),shadow,border_radius=14)
    fill=(242,236,222) if revealed else (30,37,47)
    pygame.draw.rect(screen,fill,rect,border_radius=12)
    pygame.draw.rect(screen,GOLD if selected else (72,80,93),rect,2,border_radius=12)
    inner=rect.inflate(-14,-14)
    if revealed:
        color=RED if is_red else (35,40,48)
        text(screen,fonts,'A', (rect.x+12,rect.y+10),'body',color)
        radius=max(10,min(28,rect.width//5))
        cx,cy=rect.center
        if is_red:
            pygame.draw.polygon(screen,color,[(cx,cy-radius*1.5),(cx+radius,cy),(cx,cy+radius*1.5),(cx-radius,cy)])
        else:
            pygame.draw.circle(screen,color,(cx,cy),radius)
            pygame.draw.polygon(screen,color,[(cx,cy+radius//2),(cx-radius,cy+radius*1.5),(cx+radius,cy+radius*1.5)])
        text(screen,fonts,'RED' if is_red else 'BLACK',(cx,rect.bottom-22),'tiny',color,True)
    else:
        pygame.draw.rect(screen,(67,75,89),inner,1,border_radius=8)
        clip=screen.get_clip();screen.set_clip(inner)
        for offset in range(-inner.height,inner.width,12):
            pygame.draw.line(screen,(43,52,65),(inner.x+offset,inner.top),(inner.x+offset+inner.height,inner.bottom))
        screen.set_clip(clip)
        cx,cy=rect.center
        radius=max(12,rect.width//5)
        pygame.draw.circle(screen,(25,31,39),(cx,cy),radius+7)
        pygame.draw.polygon(screen,GOLD,[(cx,cy-radius),(cx+radius,cy),(cx,cy+radius),(cx-radius,cy)],2)
        pygame.draw.circle(screen,GOLD,(cx,cy),3)


LABELS={'play':'Play now','help':'How to play','settings':'Settings','back':'Back','continue':'Continue',
        'menu':'Profile','start':'Start round','next':'Play again','quit':'Exit','pause':'Pause','resume':'Resume',
        'minus':'−','plus':'+','volume_down':'−','volume_up':'+','easy':'Easy','normal':'Normal','expert':'Expert'}


def buttons(game,layout,fonts):
    for key,rect in layout.items():
        if not key.startswith('btn_'): continue
        action=key[4:]
        selected=(action==game.settings.difficulty or action==f'turbo_{game.bet.turbo}' or action==f'avatar_{game.user.avatar_index}')
        primary=action in ('play','continue','start','next','resume')
        enabled=game.enabled(action)
        hover=game.hover_action==action
        fill=RED if primary and enabled else (45,53,64) if hover and enabled else PANEL
        border=GOLD if selected else (78,87,101) if hover else LINE
        pygame.draw.rect(game.screen,fill,rect,border_radius=10)
        pygame.draw.rect(game.screen,border,rect,2 if selected else 1,border_radius=10)
        if action.startswith('avatar_'):
            game.screen.blit(game.resources['avatars'][int(action[-1])],(rect.centerx-24,rect.centery-24))
        else:
            label=LABELS.get(action,action)
            if action.startswith('turbo_'): label='×'+action[-1]
            if action=='sound': label='Sound on' if game.settings.sound_enabled else 'Sound off'
            if action=='quit' and __import__('sys').platform=='emscripten': label='Home'
            label_color=TEXT if enabled else (89,97,108)
            if action=='play' and enabled:
                pygame.draw.polygon(game.screen,TEXT,[(rect.left+38,rect.centery-10),(rect.left+38,rect.centery+10),(rect.left+54,rect.centery)])
                text(game.screen,fonts,label.upper(),(rect.centerx+12,rect.centery),'body',label_color,True,max_width=rect.width-58)
            else:
                text(game.screen,fonts,label,rect.center,'body',label_color,True,max_width=rect.width-8)
        if game.focus_action==action:
            pygame.draw.rect(game.screen,GOLD,rect.inflate(6,6),2,border_radius=12)


def header(game,fonts):
    s=game.screen
    margin=max(16,min(48,game.w//28))
    pygame.draw.polygon(s,RED,[(margin,38),(margin+10,23),(margin+20,38),(margin+10,53)])
    text(s,fonts,'ROUGE GAGNE',(margin+30,20),'small')
    text(s,fonts,'NOIR PERD',(margin+30,41),'tiny',MUTED)
    if game.state in ('SHOW_BACKS','SHUFFLE','CHOOSE','BET_SETUP'):
        return
    if game.w>520:
        text(s,fonts,'A GAME OF FOCUS',(game.w//2,38),'tiny',MUTED,True)
    text(s,fonts,'V2.0',(game.w-margin-34,32),'tiny',GOLD)


def title(game,fonts,label,subtitle=''):
    y=96
    text(game.screen,fonts,label,(game.w//2,y+12),'title',TEXT,True,max_width=game.w-32)
    if subtitle and game.h>=500:
        text(game.screen,fonts,subtitle,(game.w//2,y+48),'small',MUTED,True,max_width=game.w-32)


def home(game,layout,fonts):
    s=game.screen;w,h=game.w,game.h
    short=h<500;wide=w>=850 and not short
    left=layout['content'].x
    if short:
        text(s,fonts,'Follow the red. Trust your focus.',(w//2,111),'title',TEXT,True)
        y=154
        for i in range(3):
            r=pygame.Rect(w//2-130+i*92,y,76,112)
            card(s,fonts,r,True,i==1)
        return
    if wide:
        text(s,fonts,'OBSERVE. TRACK. CHOOSE.',(left,120),'tiny',GOLD)
        text(s,fonts,'Follow the red.',(left,151),'hero')
        text(s,fonts,'Trust your focus.',(left,207),'hero')
        wrapped(s,fonts,'Three cards. One red. A moving challenge for your visual memory.',left,276,int(w*.38))
        hero_x=left+45
        for i in range(3): card(s,fonts,pygame.Rect(hero_x+i*114,358,98,142),True,i==1)
        history_rect=pygame.Rect(w//2+28,124,w//2-left-28,h-238)
    else:
        text(s,fonts,'Follow the red.',(w//2,121),'hero',TEXT,True)
        text(s,fonts,'Trust your focus.',(w//2,160),'hero',TEXT,True)
        text(s,fonts,'Three cards. One sharp eye.',(w//2,201),'small',MUTED,True)
        for i in range(3): card(s,fonts,pygame.Rect(w//2-139+i*97,233,84,122),True,i==1)
        history_rect=pygame.Rect(left,386,layout['content'].width,h-488)
    if history_rect.height>=90:
        panel(s,history_rect)
        text(s,fonts,'RECENT PLAYERS',(history_rect.x+20,history_rect.y+20),'tiny',GOLD)
        rows=aggregate_players(game.global_history,limit=max(1,(history_rect.height-68)//48))
        if not rows:
            wrapped(s,fonts,'Your first round starts here. Results will appear after you play.',history_rect.x+20,history_rect.y+53,history_rect.width-40,'small')
        else:
            for i,row in enumerate(rows):
                y=history_rect.y+54+i*48
                text(s,fonts,row['player'],(history_rect.x+20,y),'body',TEXT,max_width=history_rect.width-130)
                text(s,fonts,f"{row['wins']}W / {row['losses']}L",(history_rect.x+20,y+22),'tiny',MUTED)
                text(s,fonts,f"{row['goal']:+} cr",(history_rect.right-94,y+7),'body',GREEN if row['goal']>=0 else RED)


def profile(game,layout,fonts):
    title(game,fonts,'Take your seat','Your profile keeps its balance on this device.')
    r=layout['name_input']
    text(game.screen,fonts,'PLAYER NAME · 3–20 CHARACTERS',(r.x,r.y-24),'tiny',GOLD)
    pygame.draw.rect(game.screen,PANEL,r,border_radius=10)
    pygame.draw.rect(game.screen,GOLD if game.active_input else LINE,r,2,border_radius=10)
    text(game.screen,fonts,game.user.nickname or 'Enter your name',(r.x+16,r.y+15),'body',TEXT if game.user.nickname else MUTED,max_width=r.width-32)
    avatar=layout['btn_avatar_0']
    text(game.screen,fonts,'CHOOSE YOUR AVATAR',(game.w//2,avatar.y-16),'tiny',MUTED,True)
    if game.h>=500:
        text(game.screen,fonts,'30 welcome credits for each new profile.',(game.w//2,avatar.bottom+38),'small',MUTED,True,max_width=game.w-32)
        text(game.screen,fonts,'Returning players keep their saved balance.',(game.w//2,avatar.bottom+62),'small',MUTED,True,max_width=game.w-32)


def bet_screen(game,layout,fonts):
    s=game.screen;h=game.h
    title(game,fonts,'Make your move',f'{game.user.name}  ·  {game.user.balance} credits available')
    r=layout['btn_minus']
    if h<500:
        text(s,fonts,f'{game.user.balance} credits available',(game.w//2,136),'small',MUTED,True)
    text(s,fonts,str(game.bet.amount),(game.w//2,r.centery),'number',TEXT,True)
    if h>=500:
        text(s,fonts,'BASE STAKE',(game.w//2,r.y-28),'tiny',GOLD,True)
        avatar=game.resources['avatars'][game.user.avatar_index]
        s.blit(avatar,(game.w//2-154,168 if h<700 else 195))
    y=layout['btn_turbo_1'].bottom+24
    if h>=500:
        text(s,fonts,f'Total stake  {game.bet.stake()} credits',(game.w//2,y),'body',TEXT,True)
        text(s,fonts,f'{game.settings.difficulty.title()} difficulty · 10 seconds to choose',(game.w//2,y+30),'small',MUTED,True,max_width=game.w-28)
        text(s,fonts,'Find red: +stake. Miss or time out: −stake.',(game.w//2,y+55),'small',MUTED,True,max_width=game.w-28)
    else:
        text(s,fonts,f'Total {game.bet.stake()} cr · {game.settings.difficulty.title()}',(game.w//2,y-8),'small',GOLD,True)


def table(game,layout,fonts):
    s=game.screen;state=game.state
    paused=state=='PAUSE'
    actual=game.state_before_pause if paused else state
    result=state=='RESULT'
    labels={'SHOW_BACKS':('01','Remember the red','Its identity stays with the same card.'),
            'SHUFFLE':('02','Keep your eyes on it','Follow the movement.'),
            'CHOOSE':('03','Which card is red?','Tap a card or press 1, 2, 3.')}
    if result:
        label='You found it.' if game.round_result=='WIN' else 'Time ran out.' if game.selected_card_index is None else 'A close one.'
        gain=game.round_history[-1]['stake'] if game.round_history else 0
        title(game,fonts,label,f"{'+' if game.round_result=='WIN' else '−'}{gain} credits  ·  Balance {game.user.balance}")
        if game.h<500:
            text(s,fonts,f"{'+' if game.round_result=='WIN' else '−'}{gain} cr · Balance {game.user.balance}",(game.w//2,146),'small',MUTED,True)
    else:
        num,label,hint=labels.get(actual,labels['SHOW_BACKS'])
        title(game,fonts,label,hint if game.h>=500 else '')
        elapsed=(game.pause_start if paused else pygame.time.get_ticks())-game.state_start_time
        remaining=max(0,10000-elapsed)
        y=174 if game.h>=500 else 128
        width=min(420,game.w-80)
        pygame.draw.rect(s,LINE,(int((game.w-width)/2),y,int(width),3),border_radius=2)
        pygame.draw.rect(s,RED,(int((game.w-width)/2),y,round(width*remaining/10000),3),border_radius=2)
        text(s,fonts,f'{math.ceil(remaining/1000):02d}s',(game.w//2,y+23),'small',GOLD,True)
    for index,c in enumerate(game.cards):
        card(s,fonts,c.rect,c.face=='BACK',c.is_red,index==game.selected_card_index)
        if actual=='CHOOSE': text(s,fonts,str(c.slot+1),(c.rect.centerx,c.rect.bottom+23),'small',MUTED,True)
    if game.h>=500:
        text(s,fonts,f'{game.user.name}  /  {game.round_difficulty.upper()}  /  {getattr(game,"round_stake",10)} CREDITS',(game.w//2,game.h-106),'tiny',MUTED,True,max_width=game.w-24)
    if paused:
        overlay=pygame.Surface((game.w,game.h),pygame.SRCALPHA);overlay.fill((9,12,17,224));s.blit(overlay,(0,0))
        text(s,fonts,'Take a breath.',(game.w//2,game.h*.42),'hero',TEXT,True,max_width=game.w-32)
        text(s,fonts,'Your cards and timer are on hold.',(game.w//2,game.h*.42+50),'small',MUTED,True,max_width=game.w-32)


def settings_screen(game,layout,fonts):
    title(game,fonts,'Find your rhythm')
    y=layout['btn_easy'].y
    if game.h>=500:
        text(game.screen,fonts,'SHUFFLE DIFFICULTY',(game.w//2,y-26),'tiny',GOLD,True)
        text(game.screen,fonts,'Normal adapts as your winning streak grows.',(game.w//2,y+196),'small',MUTED,True,max_width=game.w-32)
    r=layout['btn_volume_down']
    text(game.screen,fonts,f'{round(game.settings.volume*100)}%',(game.w//2,r.centery),'body',TEXT,True)


def help_screen(game,layout,fonts):
    scale=1.4

    def help_text(value,pos,kind='small',color=TEXT,center=False):
        surface=fonts[kind].render(str(value),True,color)
        target=(max(1,round(surface.get_width()*scale)),max(1,round(surface.get_height()*scale)))
        surface=pygame.transform.smoothscale(surface,target)
        rect=surface.get_rect(center=pos) if center else surface.get_rect(topleft=pos)
        game.screen.blit(surface,rect)
        return rect

    def help_wrapped(value,x,y,width,kind='small',color=MUTED):
        words=value.split();line=''
        for word in words:
            candidate=(line+' '+word).strip()
            if fonts[kind].size(candidate)[0]*scale>width and line:
                help_text(line,(x,y),kind,color)
                y+=round(fonts[kind].get_linesize()*scale)+5
                line=word
            else:
                line=candidate
        if line:
            help_text(line,(x,y),kind,color)
            y+=round(fonts[kind].get_linesize()*scale)+5
        return y

    help_text('How to play',(game.w//2,108),'title',TEXT,True)
    x=layout['content'].x+10;width=layout['content'].width-20
    y=150 if game.h>=500 else 143
    items=[('01  OBSERVE','Remember the red card. You have 10 seconds.'),
           ('02  FOLLOW','The cards turn over and exchange positions for 10 seconds.'),
           ('03  CHOOSE','Select red before the 10-second timer ends. Red wins your stake; a miss or timeout loses it.')]
    for heading,body in items:
        help_text(heading,(x,y),'tiny',GOLD);y+=32
        y=help_wrapped(body,x,y,width,'small')+10
    if game.h>=500:
        y=help_wrapped('Mouse or touch to play. Tab + Enter for controls. 1 / 2 / 3 choose a card. Space pauses an active round.',x,y+4,width,'small')
        help_wrapped('Fictitious credits only. Profiles and history stay on this device; clearing browser data removes them.',x,y+8,width,'small')


def game_over(game,layout,fonts):
    title(game,fonts,'Session complete','Your saved balance is below the 10-credit minimum.')
    summary=summarize_rounds(game.round_history)
    y=200 if game.h>=500 else 178
    text(game.screen,fonts,f'{game.user.balance} credits',(game.w//2,y),'number',TEXT,True)
    text(game.screen,fonts,f"{summary['wins']} wins   /   {summary['losses']} losses   /   {summary['net']:+} net",(game.w//2,y+55),'body',MUTED,True,max_width=game.w-32)
    if game.h>=500:
        rate='—' if summary['win_rate'] is None else f"{summary['win_rate']:.0f}%"
        text(game.screen,fonts,'Win rate  '+rate,(game.w//2,y+84),'small',GOLD,True)
        text(game.screen,fonts,'You can return to choose another profile.',(game.w//2,y+105),'small',MUTED,True,max_width=game.w-32)


def draw_screen(game,layout,resources):
    fonts=resources['fonts'];s=game.screen
    s.blit(resources['background'],(0,0));header(game,fonts)
    state=game.state
    if state=='START_SCREEN': home(game,layout,fonts)
    elif state=='MENU': profile(game,layout,fonts)
    elif state=='BET_SETUP': bet_screen(game,layout,fonts)
    elif state=='HELP': help_screen(game,layout,fonts)
    elif state=='SETTINGS': settings_screen(game,layout,fonts)
    elif state=='GAME_OVER': game_over(game,layout,fonts)
    else: table(game,layout,fonts)
    buttons(game,layout,fonts)
    footer='FICTITIOUS CREDITS · LOCAL PLAY'
    if game.storage_notice: footer=game.storage_notice
    text(s,fonts,footer,(game.w//2,game.h-12),'tiny',GOLD if game.storage_notice else MUTED,True,max_width=game.w-24)
