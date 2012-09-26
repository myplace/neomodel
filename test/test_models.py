from neomodel import StructuredNode, StringProperty, IntegerProperty, ReadOnlyNode
from neomodel.core import connection_adapter


class User(StructuredNode):
    email = StringProperty(unique_index=True)
    age = IntegerProperty(index=True)


def setup():
    connection_adapter().client.clear()


def test_get():
    u = User(email='robin@test.com', age=3)
    assert u.save()
    rob = User.index.get(email='robin@test.com')
    assert rob.email == 'robin@test.com'
    assert rob.age == 3


def test_search():
    assert User(email='robin1@test.com', age=3).save()
    assert User(email='robin2@test.com', age=3).save()
    users = User.index.search(age=3)
    assert len(users)


def test_save_to_model():
    u = User(email='jim@test.com', age=3)
    assert u.save()
    assert u._node
    assert u.email == 'jim@test.com'
    assert u.age == 3


def test_unique():
    User(email='jim1@test.com', age=3).save()
    try:
        User(email='jim1@test.com', age=3).save()
    except Exception, e:
        assert e.__class__.__name__ == 'NotUnique'
    else:
        assert False


def test_update():
    user = User(email='jim2@test.com', age=3).save()
    assert user
    user.email = 'jim2000@test.com'
    user.save()
    jim = User.index.get(email='jim2000@test.com')
    assert jim
    assert jim.email == 'jim2000@test.com'


def rest_readonly_definition():
    # create user
    class MyNormalUser(StructuredNode):
        _index_name = 'readonly_test'
        name = StringProperty()
    MyNormalUser(name='bob').save()

    class MyReadOnlyUser(ReadOnlyNode):
        _index_name = 'readonly_test'
        name = StringProperty()

    # reload as readonly from same index
    bob = MyReadOnlyUser.index(name='bob')
    assert bob.name == 'bob'

    try:
        bob.name = 'tim'
    except Exception, e:
        assert e.__class__.__name__ == 'ReadOnlyError'
    else:
        assert False

    try:
        bob.delete()
    except Exception, e:
        assert e.__class__.__name__ == 'ReadOnlyError'
    else:
        assert False

    try:
        bob.save()
    except Exception, e:
        assert e.__class__.__name__ == 'ReadOnlyError'
    else:
        assert False

    try:
        bob.update()
    except Exception, e:
        assert e.__class__.__name__ == 'ReadOnlyError'
    else:
        assert False


def teardown():
    connection_adapter().client.clear()
