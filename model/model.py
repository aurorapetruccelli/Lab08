from database.impianto_DAO import ImpiantoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        lista = [] #creo la lista in cui inserirò le tuple
        for impianto in self._impianti:
            consumi = impianto.get_consumi()
            consumi_totali = []
            for consumo in consumi:
                if consumo.data.month == mese:
                    consumi_totali.append(consumo.kwh)
            media = sum(consumi_totali)/len(consumi_totali) #calcolo il consumo medio
            lista.append((impianto.nome,media))
        return lista
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        self.__ricorsione([], 1, None, 0, consumi_settimana)

        # Traduci gli ID in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [f"Giorno {giorno}: {id_to_nome[i]}" for giorno, i in enumerate(self.__sequenza_ottima, start=1)]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto, costo_corrente, consumi_settimana):
        if giorno>=8:
            #aggiorno i valori
            self.__sequenza_ottima=sequenza_parziale
            self.__costo_ottimo=costo_corrente
        else:
            costo_minore = 0
            impianto_minore = ""
            for chiave,valore in consumi_settimana.items():
                costo = valore[giorno-1]
                if ultimo_impianto != chiave and ultimo_impianto is not None:
                    costo = costo+5
                if costo<costo_minore or costo_minore==0:
                    costo_minore = costo
                    impianto_minore = chiave
            sequenza_parziale.append(impianto_minore)
            costo_corrente= costo_corrente + costo_minore
            self.__ricorsione(sequenza_parziale,giorno+1,impianto_minore,costo_corrente,consumi_settimana)
        """ Implementa la ricorsione """

    def __get_consumi_prima_settimana_mese(self, mese: int):
        dizionario = {} #creo il dizionario
        for impianto in self._impianti:
            consumi = impianto.get_consumi()
            consumi_giorno = []
            for consumo in consumi:
                if consumo.data.month == mese and 1<=consumo.data.day<= 7:
                    consumi_giorno.append(consumo.kwh)
            dizionario[impianto.id] = consumi_giorno
        return dizionario
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """

