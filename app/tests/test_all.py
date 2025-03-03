import pytest
from unittest.mock import MagicMock, patch


# Fichier clients.py
from app.crud.clients import (
    create_client, get_client, get_clients_by_commercial,
    get_all_clients, get_client_id, update_client, delete_client
)

# Fichier collaborateurs.py
from app.crud.collaborateurs import (
    create_collaborateur, authentifier_collaborateur_from_crud,
    get_collaborateur, get_all_collaborateurs,
    update_collaborateur, delete_collaborateur
)

# Fichier contrats.py
from app.crud.contrats import (
    create_contrat, get_contrat, get_contracts_by_status,
    get_all_contrats, update_contrat, delete_contrat
)

# Fichier evenements.py
from app.crud.evenements import (
    create_evenement, get_evenement, get_evenement_for_support,
    get_evenements_by_support, get_all_evenements, update_evenement
)

# --------------------------------------------------------------------
# Tests pour clients.py
# --------------------------------------------------------------------


def test_create_client():
    db = MagicMock()
    client = create_client(
        db, "Dupont", "dupont@example.com", "0123456789", "EntrepriseX", 1
    )
    db.add.assert_called_once_with(client)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(client)
    assert client.nom_complet == "Dupont"
    assert client.email == "dupont@example.com"
    assert client.nom_entreprise == "EntrepriseX"
    assert client.id_commercial == 1


def test_get_client_found():
    db = MagicMock()
    fake_client = MagicMock()
    db.query.return_value.options.return_value.filter.return_value.first.return_value = (
        fake_client
    )
    result = get_client(db, 1)
    assert result is fake_client


def test_get_clients_by_commercial():
    db = MagicMock()
    fake_clients = [MagicMock(), MagicMock()]
    db.query.return_value.filter.return_value.all.return_value = fake_clients
    result = get_clients_by_commercial(db, 1)
    assert result == fake_clients


def test_get_all_clients_commercial():
    db = MagicMock()
    fake_clients = [MagicMock()]
    db.query.return_value.filter.return_value.all.return_value = fake_clients
    result = get_all_clients(db, 1, "commercial", all_clients=False)
    assert result == fake_clients


def test_get_all_clients_non_commercial():
    db = MagicMock()
    fake_clients = [MagicMock(), MagicMock()]
    db.query.return_value.all.return_value = fake_clients
    result = get_all_clients(db, 1, "gestion", all_clients=False)
    assert result == fake_clients


def test_get_client_id():
    db = MagicMock()
    fake_client = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = fake_client
    result = get_client_id(db, 1)
    assert result is fake_client


def test_update_client_found():
    db = MagicMock()
    fake_client = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = fake_client
    updated = update_client(db, 1, nom_complet="Durand")
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(fake_client)
    assert updated is fake_client


def test_update_client_not_found():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    updated = update_client(db, 1, nom_complet="Durand")
    assert updated is None


def test_delete_client_found():
    db = MagicMock()
    fake_client = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = fake_client
    result = delete_client(db, 1)
    db.delete.assert_called_once_with(fake_client)
    db.commit.assert_called_once()
    assert result is fake_client


def test_delete_client_not_found():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    result = delete_client(db, 1)
    db.delete.assert_not_called()
    db.commit.assert_not_called()
    assert result is None

# --------------------------------------------------------------------
# Tests pour collaborateurs.py
# --------------------------------------------------------------------


def test_create_collaborateur_success():
    db = MagicMock()
    fake_departement = MagicMock()
    fake_departement.id = 10
    db.query.return_value.filter.return_value.first.return_value = (
        fake_departement
    )
    with patch(
        "app.crud.collaborateurs.Collaborateur.set_password",
        return_value="hashed"
    ):
        collaborateur = create_collaborateur(
            db, "Martin", "Paul", "paul@example.com", 10, "p.martin", "secret"
        )
    db.add.assert_called_once_with(collaborateur)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(collaborateur)
    assert collaborateur.email == "paul@example.com"
    assert collaborateur.departement_id == 10


def test_create_collaborateur_no_departement():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(ValueError) as excinfo:
        create_collaborateur(
            db, "Martin", "Paul", "paul@example.com", 999, "p.martin", "secret"
        )
    assert "Aucun département avec l'ID" in str(excinfo.value)


def test_authentifier_collaborateur_success():
    db = MagicMock()
    fake_collab = MagicMock()
    fake_collab.verify_password.return_value = True
    db.query.return_value.filter.return_value.first.return_value = fake_collab
    result = authentifier_collaborateur_from_crud(db, "login", "password")
    assert result is fake_collab


def test_authentifier_collaborateur_fail():
    db = MagicMock()
    fake_collab = MagicMock()
    fake_collab.verify_password.return_value = False
    db.query.return_value.filter.return_value.first.return_value = fake_collab
    result = authentifier_collaborateur_from_crud(db, "login", "wrongpassword")
    assert result is None


def test_get_collaborateur():
    db = MagicMock()
    fake_collab = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = fake_collab
    result = get_collaborateur(db, 1)
    assert result is fake_collab


def test_get_all_collaborateurs():
    db = MagicMock()
    fake_list = [MagicMock(), MagicMock()]
    db.query.return_value.all.return_value = fake_list
    result = get_all_collaborateurs(db)
    assert result == fake_list


def test_update_collaborateur_found():
    db = MagicMock()
    fake_collab = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = fake_collab
    updated = update_collaborateur(db, 1, email="new@example.com")
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(fake_collab)
    assert updated is fake_collab


def test_update_collaborateur_not_found():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    updated = update_collaborateur(db, 1, email="new@example.com")
    assert updated is None


def test_delete_collaborateur_found():
    db = MagicMock()
    fake_collab = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = fake_collab
    result = delete_collaborateur(db, 1)
    db.delete.assert_called_once_with(fake_collab)
    db.commit.assert_called_once()
    assert result is fake_collab


def test_delete_collaborateur_not_found():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    result = delete_collaborateur(db, 1)
    db.delete.assert_not_called()
    db.commit.assert_not_called()
    assert result is None

# --------------------------------------------------------------------
# Tests pour contrats.py
# --------------------------------------------------------------------


def test_create_contrat():
    db = MagicMock()
    contrat = create_contrat(db, id_client=1, montant_total=1000.0)
    db.add.assert_called_once_with(contrat)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(contrat)
    assert contrat.id_client == 1
    assert contrat.montant_total == 1000.0
    assert contrat.montant_restant == 1000.0
    assert contrat.statut is False


def test_get_contrat():
    db = MagicMock()
    fake_contrat = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = fake_contrat
    result = get_contrat(db, 1)
    assert result is fake_contrat


def test_get_contracts_by_status():
    db = MagicMock()
    fake_list = [MagicMock(), MagicMock()]
    db.query.return_value.filter.return_value.all.return_value = fake_list
    result = get_contracts_by_status(db, True)
    assert result == fake_list


def test_get_all_contrats():
    db = MagicMock()
    fake_list = [MagicMock(), MagicMock()]
    db.query.return_value.all.return_value = fake_list
    result = get_all_contrats(db)
    assert result == fake_list


def test_update_contrat_normal():
    db = MagicMock()
    fake_contrat = MagicMock()
    fake_contrat.statut = False
    db.query.return_value.filter.return_value.first.return_value = fake_contrat
    updated = update_contrat(db, 1, montant_total=1500.0)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(fake_contrat)
    assert updated is fake_contrat


def test_update_contrat_signed_error():
    db = MagicMock()
    fake_contrat = MagicMock()
    fake_contrat.statut = True
    db.query.return_value.filter.return_value.first.return_value = fake_contrat
    with pytest.raises(ValueError) as excinfo:
        update_contrat(db, 1, montant_total=2000.0)
    assert "Impossible de modifier le montant d'un contrat signé" in \
           str(excinfo.value)


def test_delete_contrat_found():
    db = MagicMock()
    fake_contrat = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = fake_contrat
    result = delete_contrat(db, 1)
    db.delete.assert_called_once_with(fake_contrat)
    db.commit.assert_called_once()
    assert result is fake_contrat


def test_delete_contrat_not_found():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    result = delete_contrat(db, 1)
    db.delete.assert_not_called()
    db.commit.assert_not_called()
    assert result is None

# --------------------------------------------------------------------
# Tests pour evenements.py
# --------------------------------------------------------------------


def test_create_evenement_success():
    db = MagicMock()
    fake_contrat = MagicMock()
    fake_contrat.statut = True
    db.query.return_value.filter.return_value.first.return_value = fake_contrat
    evenement = create_evenement(db, contrat_id=1, support_id=2,
                                 date_debut="2020-01-01",
                                 date_fin="2020-01-02",
                                 lieu="Paris", participants=5, notes="Test")
    db.add.assert_called_once_with(evenement)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(evenement)
    assert evenement.id_contrat == 1
    assert evenement.id_support == 2


def test_create_evenement_not_signed():
    db = MagicMock()
    fake_contrat = MagicMock()
    fake_contrat.statut = False
    db.query.return_value.filter.return_value.first.return_value = fake_contrat
    with pytest.raises(ValueError) as excinfo:
        create_evenement(db, contrat_id=1, support_id=2,
                         date_debut="2020-01-01", date_fin="2020-01-02",
                         lieu="Paris", participants=5, notes="Test")
    assert "Impossible de créer un événement pour un contrat non signé" in \
           str(excinfo.value)


def test_get_evenement():
    db = MagicMock()
    fake_event = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = fake_event
    result = get_evenement(db, 1)
    assert result is fake_event


def test_get_evenement_for_support():
    db = MagicMock()
    fake_event = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = fake_event
    result = get_evenement_for_support(db, 1, 2)
    assert result is fake_event


def test_get_evenements_by_support():
    db = MagicMock()
    fake_list = [MagicMock()]
    db.query.return_value.filter.return_value.all.return_value = fake_list
    result = get_evenements_by_support(db, 2)
    assert result == fake_list


def test_get_all_evenements():
    db = MagicMock()
    fake_list = [MagicMock(), MagicMock()]
    db.query.return_value.all.return_value = fake_list
    result = get_all_evenements(db)
    assert result == fake_list


def test_update_evenement():
    db = MagicMock()
    fake_event = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = fake_event
    updated = update_evenement(db, 1, lieu="Lyon")
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(fake_event)
    assert updated is fake_event


if __name__ == "__main__":
    pytest.main()
