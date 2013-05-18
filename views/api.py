import json

import webapp2

import settings
from utils import BaseHandler
from templatetags import naturaltime, is_new
from models import Boker, User, Like


class StreamHandler(BaseHandler):
    """
    This is basic version of simple API that return data in Json.
    TODO: Need lots of improvement or better use already API generator
    for Appengine. 
    """


    def _build_qs(self, qs={}):
        """Build querystring format from dictionary"""

        query = [('%s=%s' % (k, v)) for k, v in qs.iteritems()]
        return '&'.join(query)

    def sorter(self):
        """ Determine the sorter field used to order the result"""

        AVAILABLE_SORTERS = (
            ('likes', '-num_like'), 
            ('views', '-num_view'),
            ('comments', '-num_comment'),
            ('created', '-created'),
        )
        sorter = self.request.get('sort', 'created')
        for sort in AVAILABLE_SORTERS:
            if sorter == sort[0]:
                return sort
        return ('created', '-created')

    def get(self):

        qs = {}
        page = int(self.request.get('page') or 1)
        limit = int(self.request.get('limit') or settings.PAGINATION_LIMIT)
        sort_name, sort_field = self.sorter()
        qs['sort'] = sort_name
        bokers = Boker.all().order(sort_field)

        # Current loggedin User
        current_user = None
        if self.current_user:
            current_user = User.get_by_key_name(self.current_user['id'])

        # Filter by user
        user_filter = self.request.get('username')
        if user_filter:
            qs['username'] = user_filter
            user = User.gql("WHERE username=:1", user_filter).get()
            bokers.filter('user =', user)

        # calculate number of pages
        total = bokers.count()
        num_pages = total // limit
        if total % limit > 0:
            num_pages += 1

        # Get objects
        offset = limit*(page-1)
        bokers = bokers.run(limit=limit, offset=offset)

        # Build objects dict's
        objects = []
        for b in bokers:

            # Check if user can like a boker
            user_can_like = False
            if current_user:
                user_can_like = not Like.already_like(current_user, b)

            data = {
                'user': {
                    'id': b.user.id,
                    'username': b.user.username,
                    'name': b.user.name,
                    'url': self.uri_for('user', username=b.user.username),
                },
                'current_user': {
                    'id': None,
                    'username': None,
                },
                'photo': {
                    'key': str(b.photo.key()),
                },
                'id': b.key().id(),
                'key': str(b.key()),
                'created': naturaltime(b.created),
                'is_new': is_new(b.created),
                'description': b.description,
                'permalink': self.uri_for('boker_view', boker_id=b.key().id()),
                'num_comment': b.num_comment,
                'num_view': b.num_view,
                'num_like': b.num_like,
                'can_like': user_can_like,
            }

            if self.current_user:
                data['current_user'] = {
                    'id': self.current_user.get('id'),
                    'username': self.current_user.get('username'),
                }

            objects.append(data)

        # metadata
        qs.update({'page': page+1})
        next_qs = self._build_qs(qs)

        qs.update({'page': page-1})
        previous_qs = self._build_qs(qs)

        meta = {
            'count': len(objects),
            'limit': limit,
            'page': page,
            'next_url': '%s?%s' % (self.uri_for('streams'), next_qs) if page < num_pages else None,
            'previous_url': '%s?%s' % (self.uri_for('streams'), previous_qs) if page > 1 else None,
            'pages': num_pages,
        }

        streams = dict(
            meta=meta,
            objects=objects,
        )

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(streams))