import pytest
import services.pipeline_service as svc


class TestKonversiEmoji:
    def test_konversi_emoji_smile(self):
        result = svc.konversi_emoji("😊")
        assert ":wajah_tersenyum" in result

    def test_konversi_emoji_loudly_crying(self):
        result = svc.konversi_emoji("😭")
        assert ":wajah_menangis" in result or ":wajah_keras_menangis" in result

    def test_konversi_emoji_mixed_text(self):
        result = svc.konversi_emoji("Halo 😊 apa kabar?")
        assert ":wajah_tersenyum" in result
        assert "Halo" in result
        assert "apa kabar" in result

    def test_konversi_emoji_no_emoji(self):
        result = svc.konversi_emoji("Teks biasa tanpa emoji")
        assert result == "Teks biasa tanpa emoji"

    def test_konversi_emoji_non_string(self):
        assert svc.konversi_emoji(None) == ""
        assert svc.konversi_emoji(123) == ""
        assert svc.konversi_emoji([]) == ""


class TestHapusEmoji:
    def test_hapus_emoji_smile(self):
        result = svc.hapus_emoji("😊")
        assert result == ""

    def test_hapus_emoji_multiple(self):
        result = svc.hapus_emoji("😊😭😍")
        assert result == ""

    def test_hapus_emoji_mixed_text(self):
        result = svc.hapus_emoji("Halo 😊 apa kabar?")
        assert "Halo" in result
        assert "apa kabar" in result
        assert "😊" not in result
        assert ":wajah_tersenyum:" not in result

    def test_hapus_emoji_no_emoji(self):
        result = svc.hapus_emoji("Teks biasa tanpa emoji")
        assert result == "Teks biasa tanpa emoji"

    def test_hapus_emoji_non_string(self):
        assert svc.hapus_emoji(None) == ""
        assert svc.hapus_emoji(123) == ""
        assert svc.hapus_emoji([]) == ""


class TestRunEmojiConversion:
    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.test_data = [
            {
                "video_id": "vid1",
                "platform": "tiktok",
                "comment_sample": [
                    {"text": "Halo 😊", "user_unique_id": "user1"},
                    {"text": "Keren banget 😭🔥", "user_unique_id": "user2"},
                    {"text": "Teks biasa", "user_unique_id": "user3"},
                ],
            }
        ]

    def _reset_data(self):
        svc.set_current_data(self.test_data)

    @pytest.mark.asyncio
    async def test_convert_true(self):
        self._reset_data()
        result = await svc.run_emoji_conversion(convert_emoji=True)
        data = result["data"]
        assert result["status"] == "done"
        assert ":wajah_tersenyum" in data[0]["comment_sample"][0]["text"]
        assert ":wajah_menangis" in data[0]["comment_sample"][1]["text"] or ":wajah_keras_menangis" in data[0]["comment_sample"][1]["text"]
        assert data[0]["comment_sample"][2]["text"] == "Teks biasa"

    @pytest.mark.asyncio
    async def test_convert_false(self):
        self._reset_data()
        result = await svc.run_emoji_conversion(convert_emoji=False)
        data = result["data"]
        assert result["status"] == "done"
        assert "😊" not in data[0]["comment_sample"][0]["text"]
        assert "😭" not in data[0]["comment_sample"][1]["text"]
        assert "🔥" not in data[0]["comment_sample"][1]["text"]
        assert ":wajah_tersenyum" not in data[0]["comment_sample"][0]["text"]
        assert data[0]["comment_sample"][2]["text"] == "Teks biasa"

    @pytest.mark.asyncio
    async def test_convert_true_no_emoji(self):
        data_input = [{"video_id": "vid2", "comment_sample": [{"text": "Teks biasa saja"}]}]
        svc.set_current_data(data_input)
        result = await svc.run_emoji_conversion(convert_emoji=True)
        data = result["data"]
        assert result["status"] == "done"
        assert data[0]["comment_sample"][0]["text"] == "Teks biasa saja"

    @pytest.mark.asyncio
    async def test_convert_false_no_emoji(self):
        data_input = [{"video_id": "vid2", "comment_sample": [{"text": "Teks biasa saja"}]}]
        svc.set_current_data(data_input)
        result = await svc.run_emoji_conversion(convert_emoji=False)
        data = result["data"]
        assert result["status"] == "done"
        assert data[0]["comment_sample"][0]["text"] == "Teks biasa saja"

    @pytest.mark.asyncio
    async def test_empty_data(self):
        svc.set_current_data([])
        result = await svc.run_emoji_conversion(convert_emoji=True)
        assert result["status"] == "done"

    @pytest.mark.asyncio
    async def test_missing_comment_sample(self):
        data_input = [{"video_id": "vid3"}]
        svc.set_current_data(data_input)
        result = await svc.run_emoji_conversion(convert_emoji=True)
        assert result["status"] == "done"

    @pytest.mark.asyncio
    async def test_meta_counts(self):
        self._reset_data()
        result = await svc.run_emoji_conversion(convert_emoji=True)
        assert result["meta"]["total_videos"] == 1
        assert result["meta"]["total_comments"] == 3
