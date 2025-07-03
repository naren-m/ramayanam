import pickle
import os

from .database import Database

__all__ = ['Ramayanam']

PICKLE_FILE = os.path.join(os.path.dirname(__file__), 'ramayanam.pkl')
DB_FILE = os.path.join(os.path.dirname(__file__), 'ramayanam.db')


class AttrDict(dict):

    def __setattr__(self, attr, value):
        self[attr] = value

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(attr) from None

    def __delattr__(self, attr):
        try:
            del self[attr]
        except KeyError:
            raise AttributeError(attr) from None

    def __dir__(self):
        return list(self) + dir(dict)


class Ramayanam:
    kandaDetails = dict({
        1: {
            'id': 1,
            'name': "BalaKanda",
            'sargas': 77
        },
        2: {
            'id': 2,
            'name': "AyodhyaKanda",
            'sargas': 119
        },
        3: {
            'id': 3,
            'name': "AranyaKanda",
            'sargas': 75
        },
        4: {
            'id': 4,
            'name': "KishkindaKanda",
            'sargas': 67
        },
        5: {
            'id': 5,
            'name': "SundaraKanda",
            'sargas': 68
        },
        6: {
            'id': 6,
            'name': "YuddhaKanda",
            'sargas': 128
        }
    })

    def __init__(self):
        self.kandas = dict()

    def __iter__(self):
        for _, kanda in self.kandas.items():
            yield kanda

    def addKanda(self, kanda):
        self.kandas[kanda.number] = kanda

    def kanda(self, id):
        return self.kandas[id]

    def all(self):
        translation = list()
        for k, v in self.kandas.items():
            translation.extend(v.all())

        return translation

    def details(self):
        for _, kanda in self.kandas.items():
            print(kanda)

    @classmethod
    def load(cls, dbName=DB_FILE, pickleFile=PICKLE_FILE):

        def _readFromPickle(pickleFile):
            with open(pickleFile, 'rb') as f:
                r = pickle.load(f)
                return r

        def _readFromDB(dbName):
            r = cls()
            db = Database(dbName)

            for k, v in r.kandaDetails.items():
                kanda = Kanda.createKandaFromDict(v, db=db)
                r.addKanda(kanda)

            db.close()
            with open(PICKLE_FILE, 'wb') as f:
                pickle.dump(r, f)

            return r

        if pickleFile and os.path.exists(pickleFile):
            try:
                return _readFromPickle(pickleFile)
            except Exception as e:
                return _readFromDB(dbName)
        else:
            return _readFromDB(dbName)


class Kanda:

    def __init__(self, name, number, totalSargas):
        self.name = name
        self.number = number
        self.totalSargas = totalSargas
        self.sargas = dict()

    def __str__(self):
        return '{} has {} Sargas and a total of {} Slokas'.format(
            self.name, self.totalSargas, len(self.all()))

    def __repr__(self):
        return str(self)

    def __iter__(self):
        for _, sarga in self.sargas.items():
            yield sarga

    @property
    def id(self):
        return str(self.number)

    def addSarga(self, sarga):
        self.sargas[sarga.number] = sarga

    def sarga(self, id):
        return self.sargas[id]

    def all(self):
        translation = list()
        for k, v in self.sargas.items():
            translation.extend(v.slokas)

        return translation

    @classmethod
    def createKandaFromDict(cls, kandaMetadata, db):
        kanda = cls(name=kandaMetadata['name'],
                    number=kandaMetadata['id'],
                    totalSargas=kandaMetadata['sargas'])
        for s in range(1, kanda.totalSargas + 1):
            sarga = Sarga.loadFromDB(number=s, kanda=kanda, db=db)
            kanda.addSarga(sarga)
        return kanda


class Sarga:

    def __init__(self, number, kanda):
        self.number = number
        self.kanda = kanda
        self.slokas = dict()

    def __str__(self):
        return 'Sarga {} of {} has {} slokas'.format(self.number,
                                                     self.kanda.name,
                                                     len(self.slokas))

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self):
        for _, sloka in self.slokas.items():
            yield sloka

    @property
    def id(self):
        return '{}.{}'.format(self.kanda.id, self.number)

    def addSloka(self, sloka):
        self.slokas[sloka.number] = sloka

    def sloka(self, id):
        return self.slokas[id - 1]

    @classmethod
    def loadFromDB(cls, number, kanda, db):
        sarga = cls(number=number, kanda=kanda)
        columns = 'kanda_id, sarga_id, sloka_id, sloka, meaning, translation'
        where = 'kanda_id={} and sarga_id={}'.format(kanda.number,
                                                     number)
        rows = db.get(table='slokas', columns=columns, where=where)

        for row in rows:
            row = AttrDict(row)
            sloka = Sloka(sarga, row.sloka_id, row.sloka, row.meaning,
                          row.translation)
            sarga.addSloka(sloka)
        return sarga


class Sloka:

    def __init__(self, sarga, number, text, meaning, translation):
        self.number = number
        self.sarga = sarga

        self._text = text
        self._meaning = meaning
        self._translation = translation

    @property
    def id(self):
        return '{}.{}'.format(self.sarga.id, self.number)

    @property
    def kanda(self):
        return self.sarga.kanda

    @property
    def meaning(self):
        return self._meaning

    @property
    def translation(self):
        return self._translation

    @property
    def text(self):
        return self._text

    def __repr__(self) -> str:
        return str(self)

    def __str__(self):
        if not self.text:
            return 'Something went wrong. Debug'
        return self.text

    @classmethod
    def loadFromData(cls, sarga, number, text, meaning, translation):
        sloka = Sloka(sarga, number, text, meaning, translation)
        return sloka


if __name__ == "__main__":
    r = Ramayanam.load()

    s = r.kandas[1].sargas[1].slokas[1]

    len(r.kandas[1].sargas[8].slokas)
