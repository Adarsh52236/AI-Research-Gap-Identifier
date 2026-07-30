with open('C:/Users/adars/OneDrive/Desktop/DB_infotech/Projects/PS1-AI-Research-Gap-Identifier/backend/tests/test_authorization.py', 'a') as f:
    f.write('''

def test_duplicate_project_names_allowed_across_different_users():
    token1 = create_user_and_token("user3@example.com", "user3")
    token2 = create_user_and_token("user4@example.com", "user4")
    
    resp1 = client.post("/projects", headers={"Authorization": f"Bearer {token1}"}, json={"name": "Duplicate Name"})
    assert resp1.status_code == 201
    
    resp2 = client.post("/projects", headers={"Authorization": f"Bearer {token2}"}, json={"name": "Duplicate Name"})
    assert resp2.status_code == 201

def test_duplicate_project_names_rejected_for_same_user():
    token = create_user_and_token("user5@example.com", "user5")
    
    resp1 = client.post("/projects", headers={"Authorization": f"Bearer {token}"}, json={"name": "Unique Name"})
    assert resp1.status_code == 201
    
    resp2 = client.post("/projects", headers={"Authorization": f"Bearer {token}"}, json={"name": "Unique Name"})
    assert resp2.status_code == 409
    
    # Soft delete the first project
    proj_id = resp1.json()["id"]
    client.delete(f"/projects/{proj_id}", headers={"Authorization": f"Bearer {token}"})
    
    # Now creating the same name should work because the previous is soft-deleted
    resp3 = client.post("/projects", headers={"Authorization": f"Bearer {token}"}, json={"name": "Unique Name"})
    assert resp3.status_code == 201

def test_soft_deleted_parent_hides_child_analyses():
    token = create_user_and_token("user6@example.com", "user6")
    
    resp = client.post("/projects", headers={"Authorization": f"Bearer {token}"}, json={"name": "Project to Delete"})
    proj_id = resp.json()["id"]
    
    # Inject analysis
    db = TestingSessionLocal()
    analysis = Analysis(project_id=uuid.UUID(proj_id), query="test query")
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    analysis_id = analysis.id
    db.close()
    
    # Verify accessible
    get_resp = client.get(f"/api/v1/analyses/{analysis_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_resp.status_code == 200
    
    # Soft delete project
    client.delete(f"/projects/{proj_id}", headers={"Authorization": f"Bearer {token}"})
    
    # Verify analysis is hidden
    get_resp2 = client.get(f"/api/v1/analyses/{analysis_id}", headers={"Authorization": f"Bearer {token}"})
    assert get_resp2.status_code == 404

def test_update_after_soft_delete_returns_404():
    token = create_user_and_token("user7@example.com", "user7")
    resp = client.post("/projects", headers={"Authorization": f"Bearer {token}"}, json={"name": "Project 7"})
    proj_id = resp.json()["id"]
    
    client.delete(f"/projects/{proj_id}", headers={"Authorization": f"Bearer {token}"})
    
    update_resp = client.put(f"/projects/{proj_id}", headers={"Authorization": f"Bearer {token}"}, json={"name": "Updated 7"})
    assert update_resp.status_code == 404
''')
