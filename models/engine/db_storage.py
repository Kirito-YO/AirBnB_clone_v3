#!/usr/bin/python3
"""
moteur de base de données
"""

import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from models.base_model import Base
from models import base_model, amenity, city, place, review, state, user


class DBStorage:
    """
        gère le stockage à long terme de toutes les instances de classe
    """
    CNC = {
        'Amenity': amenity.Amenity,
        'City': city.City,
        'Place': place.Place,
        'Review': review.Review,
        'State': state.State,
        'User': user.User
    }

    """
        gère le stockage de la base de données
    """
    __engine = None
    __session = None

    def __init__(self):
        """
            ecrire le moteur self.__engine
        """
        self.__engine = create_engine(
            'mysql+mysqldb://{}:{}@{}/{}'.format(
                os.environ.get('HBNB_MYSQL_USER'),
                os.environ.get('HBNB_MYSQL_PWD'),
                os.environ.get('HBNB_MYSQL_HOST'),
                os.environ.get('HBNB_MYSQL_DB')))
        if os.environ.get("HBNB_ENV") == 'test':
            Base.metadata.drop_all(self.__engine)

    def all(self, cls=None):
        """
           renvoie un dictionnaire de tous les objets
        """
        obj_dict = {}
        if cls is not None:
            a_query = self.__session.query(DBStorage.CNC[cls])
            for obj in a_query:
                obj_ref = "{}.{}".format(type(obj).__name__, obj.id)
                obj_dict[obj_ref] = obj
            return obj_dict

        for c in DBStorage.CNC.values():
            a_query = self.__session.query(c)
            for obj in a_query:
                obj_ref = "{}.{}".format(type(obj).__name__, obj.id)
                obj_dict[obj_ref] = obj
        return obj_dict

    def new(self, obj):
        """
            ajoute des objets à la session de base de données en cours
        """
        self.__session.add(obj)

    def save(self):
        """
            engage toutes les modifications de la session de base de données en cours
        """
        self.__session.commit()

    def rollback_session(self):
        """
            rollsback une session en cas d’exception
        """
        self.__session.rollback()

    def delete(self, obj=None):
        """
            supprime obj de la session de base de données en cours si non None
        """
        if obj:
            self.__session.delete(obj)
            self.save()

    def delete_all(self):
        """
           supprime tous les objets stockés, à des fins de test
        """
        for c in DBStorage.CNC.values():
            a_query = self.__session.query(c)
            all_objs = [obj for obj in a_query]
            for obj in range(len(all_objs)):
                to_delete = all_objs.pop(0)
                to_delete.delete()
        self.save()

    def reload(self):
        """
           crée toutes les tables dans la base de données et la session à partir du moteur
        """
        Base.metadata.create_all(self.__engine)
        self.__session = scoped_session(
            sessionmaker(
                bind=self.__engine,
                expire_on_commit=False))

    def close(self):
        """
            appels remove() sur l’attribut de session privée (self.session)
        """
        self.__session.remove()

    def get(self, cls, id):
        """
            récupère un objet en fonction du nom et de l’identifiant de la classe
        """
        if cls and id:
            fetch = "{}.{}".format(cls, id)
            all_obj = self.all(cls)
            return all_obj.get(fetch)
        return None

    def count(self, cls=None):
        """
            returns the count of all objects in storage
        """
        return (len(self.all(cls)))
