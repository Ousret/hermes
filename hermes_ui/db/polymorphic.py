from . import db


def get_model_class(mapped_class_child):
    """
    Charger la classe correspondant à un chemin complet (dot package) str
    Orienté pour le champs mapped class child SQLAlchemy
    :param str mapped_class_child:
    :rtype: type
    :raise AttributeError:
    """
    decompose_type_action = mapped_class_child.split("'")  # type: list[str]

    if len(decompose_type_action) != 3 or not decompose_type_action[-2].startswith('hermes_ui.models.'):
        return None

    from sys import modules

    target_module = modules['.'.join(decompose_type_action[-2].split('.')[0:-1])]

    return getattr(target_module, decompose_type_action[-2].split('.')[-1])


def get_child_polymorphic(parent_entity):
    """
    :param db.Model parent_entity:
    :rtype: db.Model
    """
    if not hasattr(parent_entity, 'mapped_class_child') or not hasattr(parent_entity, 'id'):
        raise TypeError('Cannot uncover child entity of non SQLAlchemy object. '
                        'Should have mapped_class_child and id attr.')

    return db.session.query(get_model_class(parent_entity.mapped_class_child)).get(parent_entity.id)
