"""
Seeder command for comments app.

Seeds the database with event comments.
"""

from typing import Any, List
import random

from apps.core.management.commands.base_seeder import BaseSeederCommand
from apps.core.utils.seeding import fake, random_choice
from apps.comments.models import EventComment
from apps.events.models import Event
from apps.participants.models import EventParticipant
from apps.users.models import User


DEFAULT_COMMENT_COUNT: int = 200
DEFAULT_REPLY_RATIO: float = 0.3


class Command(BaseSeederCommand):
    """
    Seed event comment data.

    Creates comments and replies for events.
    Depends on: Events, Users, Participants.
    """

    help = 'Seed event comments'

    def add_arguments(self, parser: Any) -> None:
        """Add command arguments."""
        super().add_arguments(parser)
        parser.add_argument(
            '--count',
            type=int,
            default=DEFAULT_COMMENT_COUNT,
            help=f'Total number of comments to create (default: {DEFAULT_COMMENT_COUNT})',
        )
        parser.add_argument(
            '--reply-ratio',
            type=float,
            default=DEFAULT_REPLY_RATIO,
            help=f'Ratio of replies to top-level comments (default: {DEFAULT_REPLY_RATIO})',
        )

    def get_app_name(self) -> str:
        """Get the name of the app being seeded."""
        return 'Comments'

    def seed_data(self, **options: Any) -> int:
        """
        Seed comments.

        Args:
            **options: Command options.

        Returns:
            Number of comments created.
        """
        # Check dependencies
        self.check_dependencies({
            'Event': Event,
            'User': User,
            'EventParticipant': EventParticipant,
        })

        count: int = options.get('count', DEFAULT_COMMENT_COUNT)
        reply_ratio: float = options.get('reply_ratio', DEFAULT_REPLY_RATIO)

        comments_created = self._create_comments(count, reply_ratio)
        return comments_created

    def clear_data(self) -> None:
        """Clear all comments."""
        EventComment.objects.all().delete()

    def _create_comments(self, total_count: int, reply_ratio: float) -> int:
        """
        Create comments and replies.

        Args:
            total_count: Total number of comments to create.
            reply_ratio: Ratio of replies to top-level comments (0.0 to 1.0).

        Returns:
            Number of comments created.
        """
        events: List[Event] = list(Event.objects.all())

        if not events:
            self.stdout.write(self.style.ERROR('No events found'))
            return 0

        comments: List[EventComment] = []
        created_count: int = 0

        # Calculate splits
        top_level_count = int(total_count * (1 - reply_ratio))
        reply_count = total_count - top_level_count

        # Create top-level comments
        for _ in range(top_level_count):
            event = random_choice(events)

            # Get participants for this event
            participants = EventParticipant.objects.filter(event=event).select_related('user')
            potential_commenters = [p.user for p in participants] + [event.organizer]

            if not potential_commenters:
                continue

            user = random_choice(potential_commenters)

            comment = EventComment.objects.create(
                event=event,
                user=user,
                content=fake.paragraph(nb_sentences=random.randint(1, 4)),
            )
            comments.append(comment)
            created_count += 1

        # Create replies
        for _ in range(reply_count):
            if not comments:
                break

            parent_comment = random_choice(comments)
            event = parent_comment.event

            # Get participants for this event
            participants = EventParticipant.objects.filter(event=event).select_related('user')
            potential_commenters = [p.user for p in participants] + [event.organizer]

            if not potential_commenters:
                continue

            user = random_choice(potential_commenters)

            reply = EventComment.objects.create(
                event=event,
                user=user,
                parent=parent_comment,
                content=fake.paragraph(nb_sentences=random.randint(1, 3)),
            )
            comments.append(reply)
            created_count += 1

        self.stdout.write(
            f'  Created {created_count} comments ({top_level_count} top-level, {created_count - top_level_count} replies)'
        )
        return created_count
