from neomodel import (
    StructuredNode, StructuredRel,
    StringProperty, DateTimeProperty,
    IntegerProperty, BooleanProperty, FloatProperty,
    RelationshipTo, RelationshipFrom, Relationship,
    UniqueIdProperty,
)
from datetime import datetime


# ── Relationship models ────────────────────────────────────────────────────────

class UsesRel(StructuredRel):
    purpose = StringProperty()


class CompatibleWithRel(StructuredRel):
    notes = StringProperty()


class DependsOnRel(StructuredRel):
    pass


class AlternativeToRel(StructuredRel):
    pass


class ExtendsRel(StructuredRel):
    pass


class SimilarToRel(StructuredRel):
    score = FloatProperty(default=0.0)


# ── Node models ───────────────────────────────────────────────────────────────

TECH_TYPES = ('language', 'library', 'framework', 'tool', 'database', 'platform', 'other')
PROJECT_TYPES = (
    'web app', 'cli', 'library', 'game', 'api', 'mobile', 'desktop',
    'framework', 'database', 'devops/cloud', 'ai/ml', 'os/kernel',
    'book/tutorial', 'tool', 'other'
)


class Technology(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(unique_index=True, required=True)
    slug = StringProperty(unique_index=True, required=True)
    description = StringProperty(default='')
    url = StringProperty(default='')
    tech_type = StringProperty(choices={t: t for t in TECH_TYPES}, default='other')
    github_url = StringProperty(default='')
    documentation_url = StringProperty(default='')
    license = StringProperty(default='Unknown')
    release_year = IntegerProperty()
    is_open_source = BooleanProperty(default=True)
    created_at = DateTimeProperty(default=datetime.utcnow)

    compatible_with = Relationship('Technology', 'COMPATIBLE_WITH', model=CompatibleWithRel)
    depends_on = RelationshipTo('Technology', 'DEPENDS_ON', model=DependsOnRel)
    alternative_to = Relationship('Technology', 'ALTERNATIVE_TO', model=AlternativeToRel)
    extends = RelationshipTo('Technology', 'EXTENDS', model=ExtendsRel)
    used_by = RelationshipFrom('Project', 'USES', model=UsesRel)
    extended_by = RelationshipFrom('Technology', 'EXTENDS', model=ExtendsRel)
    has_version = RelationshipTo('TechnologyVersion', 'HAS_VERSION')
    tagged_as = RelationshipTo('Tag', 'TAGGED_AS')

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'uid': self.uid, 'name': self.name, 'slug': self.slug,
            'description': self.description, 'url': self.url, 'tech_type': self.tech_type,
        }


class Project(StructuredNode):
    uid = UniqueIdProperty()
    title = StringProperty(required=True)
    slug = StringProperty(unique_index=True, required=True)
    description = StringProperty(default='')
    url = StringProperty(default='')
    project_type = StringProperty(choices={t: t for t in PROJECT_TYPES}, default='other')
    author_username = StringProperty(default='anonymous')
    created_at = DateTimeProperty(default=datetime.utcnow)

    uses = RelationshipTo('Technology', 'USES', model=UsesRel)
    uses_version = RelationshipTo('TechnologyVersion', 'USES_VERSION')

    def __str__(self):
        return self.title

    def to_dict(self):
        return {
            'uid': self.uid, 'title': self.title, 'slug': self.slug,
            'description': self.description, 'url': self.url,
            'project_type': self.project_type, 'author_username': self.author_username,
        }


class TechnologyVersion(StructuredNode):
    uid = UniqueIdProperty()
    name = StringProperty(required=True)
    version = StringProperty(required=True)
    release_date = DateTimeProperty()


class Tag(StructuredNode):
    name = StringProperty(unique_index=True, required=True)


class User(StructuredNode):
    uid = UniqueIdProperty()
    username = StringProperty(unique_index=True, required=True)
    email = StringProperty(default='')
    created_at = DateTimeProperty(default=datetime.utcnow)

    likes = RelationshipTo('Technology', 'LIKES')
    similar_to = Relationship('User', 'SIMILAR_TO', model=SimilarToRel)