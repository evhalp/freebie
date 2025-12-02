import os
import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

from posts.models import Post, PostImage, Tag, Comment, Reaction


class Command(BaseCommand):
    help = 'Creates fake users and posts for testing'

    def handle(self, *args, **kwargs):
       
        usernames = [
            'alice_wonder', 'bob_builder', 'charlie_chef', 'diana_dancer',
            'evan_explorer', 'fiona_fitness', 'george_gamer', 'hannah_hiker',
            'ivan_inventor', 'julia_jones', 'kevin_king', 'lisa_lovely',
            'mike_music', 'nina_nature', 'oliver_outdoor', 'penny_painter',
            'quinn_quick', 'rachel_runner', 'sam_surfer', 'tina_tech',
            'uma_artist', 'victor_vlogger', 'wendy_writer', 'xander_explorer',
            'yuki_yoga', 'zara_zen', 'adam_athlete', 'bella_baker',
            'carlos_coder', 'delia_designer', 'ethan_engineer', 'faith_foodie',
            'gabe_gardener', 'hazel_hacker', 'isaac_illustrator', 'jade_juggler',
            'kyle_kayaker', 'luna_leader', 'mason_maker', 'nora_navigator',
            'owen_organizer', 'piper_photographer', 'quincy_quilter', 'ruby_reader',
            'sean_sculptor', 'tessa_traveler', 'uri_urbanist', 'vera_volunteer',
            'wade_walker', 'xena_xplorer'
        ]

        post_titles = [
            'Summer Beach Cleanup Event',
            'Community Garden Workshop',
            'Local Art Exhibition Opening',
            'Weekly Coding Meetup',
            'Morning Yoga in the Park',
            'Food Truck Festival',
            'Live Music Night',
            'Photography Walk Downtown',
            'Book Club Meeting',
            'Farmers Market Saturday',
            'Outdoor Movie Screening',
            'Charity Run for Kids',
            'Coffee & Code Morning',
            'Sunset Hike Adventure',
            'DIY Craft Workshop',
            'Local Band Showcase',
            'Community Potluck Dinner',
            'Vintage Market Day',
            'Tech Talk: AI Basics',
            'Weekend Basketball Game',
            'Painting Class for Beginners',
            'Startup Networking Event',
            'Kids Sports Day',
            'Poetry Reading Night',
            'Volunteer Park Cleanup',
            'Salsa Dancing Social',
            'Board Game Night',
            'Meditation & Mindfulness Session',
            'Street Art Tour',
            'Karaoke Night Out',
            'Plant Swap Meet',
            'Wine Tasting Evening',
            'Bike Repair Workshop',
            'Open Mic Comedy Night',
            'Beginner Rock Climbing',
            'Pottery Making Class',
            'Trivia Night at Pub',
            'Morning Bird Watching',
            'Cooking Competition',
            'Film Discussion Group',
            'Sunrise Beach Volleyball',
            'Community Theater Rehearsal',
            'Sustainable Living Workshop',
            'Pet Adoption Fair',
            'Jazz Brunch Sunday',
            'Skateboard Lessons',
            'Creative Writing Circle',
            'Picnic in the Park',
            'Language Exchange Meetup',
            'Thrift Store Treasure Hunt',
            'Acoustic Open Stage',
            'Neighborhood Block Party',
            'Fitness Boot Camp',
            'Astronomy Night',
            'Salad Making Workshop',
            'Graffiti Art Session',
            'Frisbee Tournament',
            'Tea Tasting Afternoon',
            'Dance Fitness Class',
            'Skateboard Demo Day',
            'Knitting Circle',
            'Chess in the Park',
            'Mobile Gaming Tournament',
            'Stand Up Paddleboarding',
            'Improv Theater Workshop',
            'Rooftop Barbecue',
            'Photography Exhibition',
            'Sidewalk Chalk Art',
            'Smoothie Making Class',
            'Local History Walk',
            'Parkour Training Session',
            'Pottery Painting Party',
            'Vintage Vinyl Listening',
            'Soccer Pickup Game',
            'Cupcake Decorating',
            'Tai Chi in Park',
            'Craft Beer Tasting',
            'Mural Painting Project',
            'Tennis Doubles Match',
            'Homemade Pasta Workshop',
            'Drone Flying Demo',
            'Roller Skating Social',
            'Terrarium Making Class',
            'Ping Pong Tournament',
            'Kombucha Brewing 101',
            'Street Photography Walk',
            'Kickboxing Class',
            'Ukulele Learning Circle',
            'Urban Sketching Meetup',
            'Beach Bonfire Night',
            'Bread Baking Workshop',
            'Outdoor Bootcamp',
            'Makers Market',
            'Calligraphy Workshop',
            'Disc Golf Tournament',
            'Smoothie Bowl Cafe',
            'Parkour Jam Session',
            'Vegan Cooking Class'
        ]

        locations = [
            'Central Park', 'Community Center', 'Downtown Plaza',
            'Riverside Park', 'City Library', 'Main Street Gallery',
            'Beachfront', 'Highland Trail', 'Coffee House',
            'Sports Complex', 'Art Studio', 'Tech Hub',
            'Garden District', 'Market Square', 'University Campus'
        ]

        descriptions = [
            'Join us for an amazing community event! Everyone is welcome.',
            'Come together with neighbors for this special gathering.',
            'Don\'t miss out on this exciting opportunity to connect.',
            'Bring your friends and family to this fun-filled event.',
            'We\'re excited to host this event and see you there!',
            'Looking forward to a great time with the community.',
            'All skill levels welcome - come as you are!',
            'Free event open to all ages. Refreshments provided.',
            'Registration recommended but walk-ins accepted.',
            'Limited spots available, sign up early!'
        ]

        bios = [
            'Outdoor enthusiast and community organizer. Always looking for the next adventure!',
            'Tech professional by day, event planner by night. Love bringing people together.',
            'Fitness lover and healthy living advocate. Let\'s get moving!',
            'Local artist passionate about creative community spaces.',
            'Foodie, photographer, and part-time explorer. Living life one event at a time.',
            'Environmental activist working to make our community greener.',
            'Music lover and concert goer. Always down for live performances!',
            'Book nerd and coffee addict. Let\'s discuss literature over lattes.',
            'Sports enthusiast and weekend warrior. Competition is my middle name.',
            'Yoga instructor and wellness coach. Mind, body, and community.',
            'Amateur chef hosting cooking classes and potlucks.',
            'Startup founder interested in tech and networking events.',
            'Parent of two looking to connect with other families in the area.',
            'Photographer capturing the beauty of our community.',
            'Volunteer coordinator passionate about giving back.',
        ]

       
        images_dir = os.path.join(settings.MEDIA_ROOT, 'post/images')
        image_files = []
        
        if os.path.exists(images_dir):
            for filename in os.listdir(images_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    image_files.append(filename)
        
        if not image_files:
            self.stdout.write(self.style.WARNING('No images found in media/post/images'))
            return

       
        user_images_dir = os.path.join(settings.MEDIA_ROOT, 'user/images')
        user_image_files = []
        
        if os.path.exists(user_images_dir):
            for filename in os.listdir(user_images_dir):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    user_image_files.append(filename)
        
        self.stdout.write(f'Found {len(image_files)} post images')
        self.stdout.write(f'Found {len(user_image_files)} user profile images')

       
        created_users = []
        for idx, username in enumerate(usernames[:50]): 
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@example.com',
                    password='testpass123',
                    first_name=username.split('_')[0].capitalize(),
                    last_name=username.split('_')[1].capitalize()
                )
                
               
                profile = user.userprofile
                profile.bio = bios[idx % len(bios)]
                
               
                if user_image_files:
                    profile.image = f'user/images/{user_image_files[idx % len(user_image_files)]}'
                
                profile.save()
                
                created_users.append(user)
                self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
        
        if not created_users:
            created_users = list(User.objects.all()[:50])

        tag_names = ['community', 'outdoor', 'social', 'fitness', 'art', 'tech', 'food', 'music']
        tags = []
        for tag_name in tag_names:
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={
                    'slug': tag_name,
                    'description': f'{tag_name.capitalize()} related events',
                    'bg_color': f'#{"".join([random.choice("0123456789ABCDEF") for _ in range(6)])}',
                    'text_color': '#FFFFFF'
                }
            )
            tags.append(tag)

       
        used_images = set()
        posts_created = 0
        
        for i, title in enumerate(post_titles):
            user = random.choice(created_users)
            
            if i < 10:
                hours_ago = random.randint(1, 3)
                start_time = timezone.now() - timedelta(hours=hours_ago)
                end_time = timezone.now() + timedelta(hours=random.randint(1, 4))
            else:
                days_ahead = random.randint(1, 30)
                start_time = timezone.now() + timedelta(days=days_ahead, hours=random.randint(8, 18))
                end_time = start_time + timedelta(hours=random.randint(1, 4))
            
            post = Post.objects.create(
                user=user,
                title=title,
                description=random.choice(descriptions),
                location=random.choice(locations),
                start_time=start_time,
                end_time=end_time
            )
            
           
            post.tags.set(random.sample(tags, k=random.randint(1, 3)))
            
           
            num_images = random.randint(1, min(3, len(image_files)))
            available_images = [img for img in image_files if img not in used_images]
            
            if not available_images:
                available_images = image_files
                used_images.clear()
            
            selected_images = random.sample(available_images, min(num_images, len(available_images)))
            
            for idx, image_filename in enumerate(selected_images):
                PostImage.objects.create(
                    post=post,
                    image=f'post/images/{image_filename}',
                    order=idx,
                    caption=f'{title} - Photo {idx + 1}'
                )
                used_images.add(image_filename)
            
           
            num_comments = random.randint(0, 5)
            commenters = random.sample(created_users, min(num_comments, len(created_users)))
            
            comment_texts = [
                'This looks amazing! Count me in!',
                'Can\'t wait for this event!',
                'Thanks for organizing this!',
                'What time should we arrive?',
                'Is parking available nearby?',
                'Sounds like fun!',
                'I\'ll bring some friends!',
                'Great initiative!',
            ]
            
            for commenter in commenters:
                Comment.objects.create(
                    post=post,
                    user=commenter,
                    content=random.choice(comment_texts),
                    created_at=timezone.now() - timedelta(days=random.randint(0, 7))
                )
            
            posts_created += 1
            self.stdout.write(self.style.SUCCESS(f'Created post: {title}'))
        
       
        for user in created_users:
           
            other_users = [u for u in created_users if u != user]
            to_follow = random.sample(other_users, k=random.randint(3, 8))
            for target in to_follow:
                user.userprofile.follow(target.userprofile)
            
           
            all_posts = Post.objects.all()
            posts_to_react = random.sample(list(all_posts), k=min(10, len(all_posts)))
            
            for post in posts_to_react:
                if random.random() > 0.3: 
                    Reaction.objects.get_or_create(
                        post=post,
                        user=user,
                        defaults={
                            'sentiment': random.choice(['LIKE', None]),
                            'is_attending': random.choice([True, False])
                        }
                    )

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created:'))
        self.stdout.write(f'- {len(created_users)} users')
        self.stdout.write(f'- {posts_created} posts')
        self.stdout.write(f'- {len(tags)} tags')
        self.stdout.write(self.style.SUCCESS('\nTest data creation complete!'))