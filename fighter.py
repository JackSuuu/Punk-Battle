import pygame


class Fighter:
    def __init__(self, player, x, y, flip, data: list, sprite_sheet, animation_steps):
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        # use constructor to add parameter into methods and return back
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        # Convert it into a dict if further implementation needed
        # index => {'attack_1': 0, 'attack_2': 1, 'death': 2, 'fall': 3, 'idle': 4, 'jump': 5, 'run': 6, 'hit': 7}
        self.action = 4
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 100, 200))
        self.velocity_y = 0
        # Trigger for the action that the fighter is performing
        self.running = False
        self.jump = False
        self.attacking = False  # A trigger detect if attacking
        self.attack_type = 0
        self.attack_cooldown = 0
        # self.attack_sound = sound -> for the effect trigger when certain action perform
        self.hit = False
        self.health = 100
        self.alive = True

    def load_images(self, sprite_sheet, animation_steps):
        # Load images from sprite sheets
        animation_list = []
        for y, animation in enumerate(animation_steps):  # Enumerate() -> index & each
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size,
                                                   self.size, self.size)
                temp_img_list.append(pygame.transform.scale(temp_img, (self.size * self.image_scale,
                                                                       self.size * self.image_scale)))
            animation_list.append(temp_img_list)
        return animation_list

    def movement(self, screen_width: int, screen_height: int, surface, target):
        speed = 10
        gravity = 2
        d_x = 0
        d_y = 0
        self.running = False
        self.attack_type = 0

        # Get all KEY ABLE TO PRESS in pygame
        key = pygame.key.get_pressed()

        # Can only perform other actions if not currently attacking
        if not self.attacking and self.alive:
            # Check player 1 controls
            if self.player == 1:
                # Movement
                if key[pygame.K_a]:
                    d_x = -speed
                    self.running = True
                if key[pygame.K_d]:
                    d_x = speed
                    self.running = True
                # Jump
                if key[pygame.K_w] and not self.jump:
                    self.jump = True
                    self.velocity_y = -30
                # Attack Mechanism
                if key[pygame.K_e] or key[pygame.K_r]:
                    self.attack(surface, target)
                    # Determine which attack type was used
                    if key[pygame.K_j]:
                        self.attack_type = 1
                    else:
                        self.attack_type = 2
            elif self.player == 2:
                # Movement
                if key[pygame.K_LEFT]:
                    d_x = -speed
                    self.running = True
                if key[pygame.K_RIGHT]:
                    d_x = speed
                    self.running = True
                # Jump
                if key[pygame.K_UP] and not self.jump:
                    self.jump = True
                    self.velocity_y = -30
                # Attack Mechanism
                if key[pygame.K_n] or key[pygame.K_m]:
                    self.attack(surface, target)
                    # Determine which attack type was used
                    if key[pygame.K_n]:
                        self.attack_type = 1
                    else:
                        self.attack_type = 2

        # Apply gravity in order for player drops
        self.velocity_y += gravity
        d_y += self.velocity_y

        # Ensure player stay on the screen
        if self.rect.left + d_x < 0:
            # "Edge" minus "the distance to the edge" of the screen
            d_x = 0 - self.rect.left
        if self.rect.right + d_x > screen_width:
            d_x = screen_width - self.rect.right
        if self.rect.bottom + d_y > screen_height - 110:
            self.jump = False
            self.velocity_y = 0
            d_y = screen_height - 110 - self.rect.bottom

        # Ensure players face each other
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        # Apply attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Update player position
        self.rect.x += d_x
        self.rect.y += d_y

    # Handle animation updates
    def update(self):
        # Check what action the player is performing
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(2)  # Death
        elif self.hit:
            self.update_action(7)  # Get hit
        elif self.attacking:
            if self.attack_type == 1:
                self.update_action(0)  # Attack 1
            elif self.attack_type == 2:
                self.update_action(1)  # Attack 2
        elif self.jump:
            self.update_action(5)  # jump
        elif self.running:
            self.update_action(6)  # run
        else:
            self.update_action(4)  # idle

        animation_cooldown = 100  # ms
        # Update image
        self.image = self.animation_list[self.action][self.frame_index]
        # Check if enough time has passed since the last update --> current_time - created_time
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        # Check if the animation has finished
        if self.frame_index >= len(self.animation_list[self.action]):
            # If the player is dead then end the animation
            if not self.alive:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                # Check if an attack was executed
                if self.action == 0 or self.action == 1:
                    self.attacking = False
                    self.attack_cooldown = 20
                # Check if damage was taken
                if self.action == 7:
                    self.hit = False
                    # If the player was in the middle of an attack, then it should stop
                    self.attacking = False
                    self.attack_cooldown = 20

    def attack(self, surface, target):  # target: Fighter
        if self.attack_cooldown == 0:
            self.attacking = True
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip),
                                         self.rect.y, 2 * self.rect.width, self.rect.height)
            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True

            # pygame.draw.rect(surface, (0, 255, 0), attacking_rect)  # The green test rectangle

    def update_action(self, new_action):
        # Check if the new action is different to the previous one
        if new_action != self.action:
            self.action = new_action
            # Update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)  # Flip direction
        # pygame.draw.rect(surface, (255, 255, 0), self.rect) --> The rectangle for development
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale),
                                  self.rect.y - (self.offset[1] * self.image_scale)))

