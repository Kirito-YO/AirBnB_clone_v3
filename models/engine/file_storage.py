#!/usr/bin/python3
"""
Gère les E/S, l’écriture et la lecture, de JSON pour le stockage de toutes les instances de classe
"""
import json
from models import base_model, amenity, city, place, review, state, user
from datetime import datetime

strptime = datetime.strptime
to_json = base_model.BaseModel.to_json


class FileStorage:
    """
        gère le stockage à long terme de toutes les instances de classe
    """
    CNC = {
        'BaseModel': base_model.BaseModel,
        'Amenity': amenity.Amenity,
        'City': city.City,
        'Place': place.Place,
        'Review': review.Review,
        'State': state.State,
        'User': user.User
    }
    
    __file_path = './dev/file.json'
    __objects = {}

    def all(self, cls=None):
        """
            returns private attribute: __objects
        """
        if cls is not None:
            new_objs = {}
            for clsid, obj in FileStorage.__objects.items():
                if type(obj).__name__ == cls:
                    new_objs[clsid] = obj
            return new_objs
        else:
            return FileStorage.__objects

    def new(self, obj):

        bm_id = "{}.{}".format(type(obj).__name__, obj.id)
        FileStorage.__objects[bm_id] = obj

    def save(self):

        fname = FileStorage.__file_path
        storage_d = {}
        for bm_id, bm_obj in FileStorage.__objects.items():
            storage_d[bm_id] = bm_obj.to_json(saving_file_storage=True)
        with open(fname, mode='w', encoding='utf-8') as f_io:
            json.dump(storage_d, f_io)

    def reload(self):
        """
            si le fichier existe, désérialise le fichier JSON en __objets, sinon rien
        """
        fname = FileStorage.__file_path
        FileStorage.__objects = {}
        try:
            with open(fname, mode='r', encoding='utf-8') as f_io:
                new_objs = json.load(f_io)
        except:
            return
        for o_id, d in new_objs.items():
            k_cls = d['__class__']
            FileStorage.__objects[o_id] = FileStorage.CNC[k_cls](**d)

    def delete(self, obj=None):
        """
            supprime obj from __objects s’il est à l’intérieur
        """
        if obj:
            obj_ref = "{}.{}".format(type(obj).__name__, obj.id)
            all_class_objs = self.all(obj.__class__.__name__)
            if all_class_objs.get(obj_ref):
                del FileStorage.__objects[obj_ref]
            self.save()

    def delete_all(self):
        """
            supprime tous les objets stockés, à des fins de test
        """
        try:
            with open(FileStorage.__file_path, mode='w') as f_io:
                pass
        except:
            pass
        del FileStorage.__objects
        FileStorage.__objects = {}
        self.save()

    def close(self):
        """
            appelle la méthode reload() pour la désérialisation de JSON aux objets
        """
        self.reload()

    def get(self, cls, id):
        """
            récupère un objet en fonction du nom et de l’identifiant de la classe
        """
        if cls and id:
            fetch_obj = "{}.{}".format(cls, id)
            all_obj = self.all(cls)
            return all_obj.get(fetch_obj)
        return None

    def count(self, cls=None):
        """
        nombre de tous les objets stockés
        """
        return (len(self.all(cls)))
