import tkinter as tk
import tkinter.messagebox as messagebox
import random
import numpy as np
import pygame

class DreamcatcherGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Dreamcatcher: The AI's Quest")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        pygame.mixer.init()

        self.start_sound = pygame.mixer.Sound("start.mp3")
        self.success_sound = pygame.mixer.Sound("success.mp3")
        self.failure_sound = pygame.mixer.Sound("failure.mp3")

        self.canvas = tk.Canvas(self.root, width=800, height=600, bg="lightblue")
        self.canvas.pack()

        self.player = self.canvas.create_oval(375, 275, 425, 325, fill="gold", outline="black", width=2)
        self.player_speed = 10

        self.dream_fragments = []
        self.nightmares = []
        self.num_fragments = 15
        self.num_nightmares = 10

        self.highest_score = 0 

        self.reset_game()

    def reset_game(self):
        self.start_sound.play(loops=-1)
        self.canvas.delete("all")
        self.player = self.canvas.create_oval(375, 275, 425, 325, fill="gold", outline="black", width=2)
        self.dream_fragments = []
        self.nightmares = []
        self.score = 0
        self.score_text = self.canvas.create_text(50, 20, text=f"Score: {self.score}", font=("Arial", 14), fill="black")
        self.time_left = 60
        self.timer_text = self.canvas.create_text(750, 20, text=f"Time: {self.time_left}", font=("Arial", 14), fill="black")
        self.game_over = False

        for _ in range(self.num_fragments):
            x = random.randint(50, 750)
            y = random.randint(50, 550)
            fragment = {'id': self.canvas.create_oval(x-10, y-10, x+10, y+10, fill="green", outline="black"),
                        'dx': random.choice([-5, 5]),
                        'dy': random.choice([-5, 5])}
            self.dream_fragments.append(fragment)

        for _ in range(self.num_nightmares):
            x = random.randint(50, 750)
            y = random.randint(50, 550)
            nightmare = {'id': self.canvas.create_rectangle(x-15, y-15, x+15, y+15, fill="red", outline="black"),
                         'dx': random.choice([-5, 5]),
                         'dy': random.choice([-5, 5])}
            self.nightmares.append(nightmare)

        self.update_timer()
        self.move_shapes()

        self.prompt_user_choice()

    def prompt_user_choice(self):
        choice = messagebox.askyesno("Choose Player", "Do you want the AI to play? (Yes) or play yourself? (No)")
        if choice:
            self.simple_reflex_agent()
        else:
            self.enable_manual_play()

    def enable_manual_play(self):
        self.root.bind("<Up>", lambda event: (print("Up key pressed"), self.move_player(0, -self.player_speed)))
        self.root.bind("<Down>", lambda event: (print("Down key pressed"), self.move_player(0, self.player_speed)))
        self.root.bind("<Left>", lambda event: (print("Left key pressed"), self.move_player(-self.player_speed, 0)))
        self.root.bind("<Right>", lambda event: (print("Right key pressed"), self.move_player(self.player_speed, 0)))
        self.canvas.focus_set()
        self.root.focus_force()

    def simple_reflex_agent(self):
        if self.game_over:
            return

        closest_fragment = self.get_closest(self.player, self.dream_fragments)
        if closest_fragment:
            self.move_towards(self.player, closest_fragment)

        self.root.after(100, self.simple_reflex_agent)

    def get_closest(self, player, fragments):
        min_dist = float("inf")
        closest_fragment = None
        player_coords = self.canvas.coords(player)
        for fragment in fragments:
            fragment_coords = self.canvas.coords(fragment['id'])
            dist = self.distance(player_coords, fragment_coords)
            if dist < min_dist:
                min_dist = dist
                closest_fragment = fragment
        return closest_fragment

    def distance(self, coords1, coords2): # Based on Euclidean distance
        return ((coords1[0] - coords2[0]) ** 2 + (coords1[1] - coords2[1]) ** 2) ** 0.5

    def move_towards(self, player, fragment): # AI Related Movement
        player_coords = self.canvas.coords(player)
        fragment_coords = self.canvas.coords(fragment['id'])

        dx = np.sign(fragment_coords[0] - player_coords[0]) * self.player_speed
        dy = np.sign(fragment_coords[1] - player_coords[1]) * self.player_speed
        self.canvas.move(player, dx, dy)

    def move_player(self, dx, dy): # Manual Movement
        if not self.game_over:
            player_coords = self.canvas.coords(self.player)

            if player_coords[0] + dx < 0:
                dx = -player_coords[0]
            elif player_coords[2] + dx > 800:
                dx = 800 - player_coords[2]
            if player_coords[1] + dy < 0:
                dy = -player_coords[1]
            elif player_coords[3] + dy > 600:
                dy = 600 - player_coords[3]

            self.canvas.move(self.player, dx, dy)
            self.check_collisions()

    def check_collisions(self):
        if not self.game_over:
            for fragment in self.dream_fragments[:]:
                if self.is_collision(self.player, fragment['id']):
                    self.dream_fragments.remove(fragment)
                    self.canvas.delete(fragment['id'])
                    self.score += 10
                    self.update_score()
                    if not self.dream_fragments:
                        self.end_game("You Win! All green fragments eaten!", color="green")
                        return

            for nightmare in self.nightmares:
                if self.is_collision(self.player, nightmare['id']):
                    self.score -= 1
                    self.update_score()

    def is_collision(self, player, item): # axis-aligned bounding box (AABB) collision detection
        player_coords = self.canvas.coords(player)
        item_coords = self.canvas.coords(item)

        return not (player_coords[2] < item_coords[0] or player_coords[0] > item_coords[2] or
                    player_coords[3] < item_coords[1] or player_coords[1] > item_coords[3])
        '''
            Player is to the left of the item: player_coords[2] < item_coords[0]
            Player is to the right of the item: player_coords[0] > item_coords[2]
            Player is above the item: player_coords[3] < item_coords[1]
            Player is below the item: player_coords[1] > item_coords[3]
        '''

    def update_score(self):
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")

    def move_shapes(self): # iterates over dream_fragments and nightmares
        if not self.game_over:
            for fragment in self.dream_fragments:
                self.move_shape(fragment)

            for nightmare in self.nightmares:
                self.move_shape(nightmare)

            self.check_collisions()

            self.root.after(50, self.move_shapes)

    def move_shape(self, shape): # moves it and handles boundary collisions.
        self.canvas.move(shape['id'], shape['dx'], shape['dy'])
        coords = self.canvas.coords(shape['id'])

        if coords[0] <= 0 or coords[2] >= 800:
            shape['dx'] = -shape['dx']

        if coords[1] <= 0 or coords[3] >= 600:
            shape['dy'] = -shape['dy']

    def update_timer(self):
        if not self.game_over:
            if self.time_left > 0:
                self.time_left -= 1
                self.canvas.itemconfig(self.timer_text, text=f"Time: {self.time_left}")
                self.root.after(1000, self.update_timer)
            else:
                if self.dream_fragments:
                    self.end_game("Game Over! Time's up!")

    def end_game(self, message, color="red"):
        self.game_over = True
        self.canvas.create_text(400, 300, text=message, font=("Arial", 24), fill=color)
        if self.score > self.highest_score:
            self.highest_score = self.score
        self.canvas.create_text(400, 350, text=f"Highest Score: {self.highest_score}", font=("Arial", 18), fill="blue")
        self.root.after(2000, self.prompt_play_again)

        self.start_sound.stop()

        if message.startswith("You Win"):
            self.success_sound.play()
        else:
            self.failure_sound.play()

    def prompt_play_again(self):
        play_again = messagebox.askyesno("Game Over", "Do you want to play again?")
        if play_again:
            self.reset_game()
        else:
            self.root.destroy()

root = tk.Tk()
game = DreamcatcherGame(root)
root.mainloop()
