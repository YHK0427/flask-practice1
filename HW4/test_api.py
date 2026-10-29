import os
import unittest

# app.py 를 가져오기 전에 정해야 메모리 DB 를 씁니다. instance/todo.db 를 건드리지 않습니다.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
import app as todo_app          # 2차시에 친 app.py 를 가져온다


class TodoApiTest(unittest.TestCase):
    def setUp(self):             # 테스트 하나마다 먼저 돈다
        todo_app.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        todo_app.app.config["TESTING"] = True
        self.client = todo_app.app.test_client()
        self.ctx = todo_app.app.app_context()
        self.ctx.push()
        todo_app.db.drop_all()
        todo_app.db.create_all()

    def tearDown(self):          # 끝날 때마다 돈다
        todo_app.db.session.remove()
        self.ctx.pop()

    def test_만든_것이_목록에_그대로_나온다(self):
        self.client.post("/api/todos/", json={"text": "우유사기", "done": True})
        self.client.post("/api/todos/", json={"text": "책반납"})
        r = self.client.get("/api/todos/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.get_json()), 2)     # 둘 다 나와야 한다

    def test_만들면_201_과_만들어진_것이_온다(self):
        r = self.client.post("/api/todos/", json={"text": "우유사기"})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.get_json()["text"], "우유사기")

    def test_없는_번호는_404_다(self):
        r = self.client.get("/api/todos/999")
        self.assertEqual(r.status_code, 404)
        self.assertEqual(r.get_json()["message"], "999 번 할 일이 없습니다")

    def test_patch_는_보낸_칸만_바꾼다(self):
        made = self.client.post("/api/todos/", json={"text": "책반납", "note": "도서관"}).get_json()
        r = self.client.patch(f"/api/todos/{made['id']}", json={"done": True})
        self.assertEqual(r.get_json()["text"], "책반납")    # 글자는 그대로
        self.assertEqual(r.get_json()["note"], "도서관")    # 설명도 그대로
        self.assertTrue(r.get_json()["done"])               # 완료만 바뀜

    def test_지우면_204_고_다시_찾으면_404_다(self):
        made = self.client.post("/api/todos/", json={"text": "지울것"}).get_json()
        self.assertEqual(self.client.delete(f"/api/todos/{made['id']}").status_code, 204)
        self.assertEqual(self.client.get(f"/api/todos/{made['id']}").status_code, 404)

    def test_note_를_주면_그대로_안_주면_빈_글자(self):
        r = self.client.post("/api/todos/", json={"text": "우유사기", "note": "2리터짜리로"})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.get_json()["note"], "2리터짜리로")
        r = self.client.post("/api/todos/", json={"text": "책반납"})
        self.assertEqual(r.get_json()["note"], "")

    def test_done_으로_걸러_받는다(self):
        self.client.post("/api/todos/", json={"text": "우유사기", "done": True})
        self.client.post("/api/todos/", json={"text": "책반납"})
        done = self.client.get("/api/todos/?done=true").get_json()
        todo = self.client.get("/api/todos/?done=false").get_json()
        self.assertEqual([t["text"] for t in done], ["우유사기"])
        self.assertEqual([t["text"] for t in todo], ["책반납"])


if __name__ == "__main__":
    unittest.main()
