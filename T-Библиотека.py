import json
import os
from datetime import datetime

class Book:
    """Класс для представления книги"""
    
    def __init__(self, title, author, genre, year, description):
        self.id = datetime.now().timestamp()  # уникальный идентификатор
        self.title = title
        self.author = author
        self.genre = genre
        self.year = year
        self.description = description
        self.status = "не прочитана"  # по умолчанию
        self.favorite = False  # в избранном или нет
    
    def to_dict(self):
        """Преобразует объект книги в словарь для сохранения в JSON"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'genre': self.genre,
            'year': self.year,
            'description': self.description,
            'status': self.status,
            'favorite': self.favorite
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создает объект книги из словаря"""
        book = cls(data['title'], data['author'], data['genre'], 
                   data['year'], data['description'])
        book.id = data['id']
        book.status = data['status']
        book.favorite = data['favorite']
        return book
    
    def __str__(self):
        """Строковое представление книги"""
        fav_mark = "⭐ " if self.favorite else ""
        return f"{fav_mark}{self.title} | {self.author} | {self.genre} | {self.year} | {self.status}"


class Library:
    """Класс для управления библиотекой"""
    
    def __init__(self, filename='library.json'):
        self.filename = filename
        self.books = []
        self.load_from_file()
    
    def add_book(self, title, author, genre, year, description):
        """Добавляет новую книгу в библиотеку"""
        book = Book(title, author, genre, year, description)
        self.books.append(book)
        self.save_to_file()
        print(f"\n✅ Книга '{title}' успешно добавлена!")
        return book
    
    def delete_book(self, book_id):
        """Удаляет книгу из библиотеки по ID"""
        for i, book in enumerate(self.books):
            if book.id == book_id:
                deleted_title = book.title
                del self.books[i]
                self.save_to_file()
                print(f"\n✅ Книга '{deleted_title}' удалена!")
                return True
        print("\n❌ Книга с таким ID не найдена!")
        return False
    
    def get_all_books(self):
        """Возвращает список всех книг"""
        return self.books
    
    def find_book_by_id(self, book_id):
        """Находит книгу по ID"""
        for book in self.books:
            if book.id == book_id:
                return book
        return None
    
    def toggle_favorite(self, book_id):
        """Добавляет или удаляет книгу из избранного"""
        book = self.find_book_by_id(book_id)
        if book:
            book.favorite = not book.favorite
            status = "добавлена в избранное" if book.favorite else "удалена из избранного"
            print(f"\n✅ Книга '{book.title}' {status}!")
            self.save_to_file()
            return True
        print("\n❌ Книга с таким ID не найдена!")
        return False
    
    def change_status(self, book_id, status):
        """Изменяет статус книги"""
        if status not in ['прочитана', 'не прочитана']:
            print("\n❌ Некорректный статус! Используйте 'прочитана' или 'не прочитана'")
            return False
        
        book = self.find_book_by_id(book_id)
        if book:
            book.status = status
            print(f"\n✅ Статус книги '{book.title}' изменен на '{status}'!")
            self.save_to_file()
            return True
        print("\n❌ Книга с таким ID не найдена!")
        return False
    
    def get_favorites(self):
        """Возвращает список избранных книг"""
        return [book for book in self.books if book.favorite]
    
    def search_books(self, keyword):
        """Ищет книги по ключевому слову в названии, авторе или описании"""
        keyword = keyword.lower()
        results = []
        for book in self.books:
            if (keyword in book.title.lower() or 
                keyword in book.author.lower() or 
                keyword in book.description.lower()):
                results.append(book)
        return results
    
    def sort_books(self, key='title', reverse=False):
        """Сортирует книги по указанному ключу"""
        valid_keys = {
            'название': 'title',
            'автор': 'author', 
            'год': 'year',
            'жанр': 'genre'
        }
        
        sort_key = valid_keys.get(key.lower(), 'title')
        
        if sort_key == 'year':
            return sorted(self.books, key=lambda x: int(x.year) if x.year.isdigit() else 0, reverse=reverse)
        else:
            return sorted(self.books, key=lambda x: getattr(x, sort_key).lower(), reverse=reverse)
    
    def filter_books(self, filter_type, value):
        """Фильтрует книги по жанру или статусу"""
        if filter_type == 'жанр':
            return [book for book in self.books if book.genre.lower() == value.lower()]
        elif filter_type == 'статус':
            return [book for book in self.books if book.status.lower() == value.lower()]
        else:
            return []
    
    def get_recommendations(self):
        """Возвращает рекомендации на основе избранных книг"""
        if not self.books:
            return []
        
        favorites = self.get_favorites()
        if not favorites:
            # Если нет избранных, рекомендуем самые новые или случайные книги
            return sorted(self.books, key=lambda x: x.year, reverse=True)[:5]
        
        # Анализируем жанры из избранного
        favorite_genres = {}
        for book in favorites:
            favorite_genres[book.genre] = favorite_genres.get(book.genre, 0) + 1
        
        # Находим самый популярный жанр
        top_genre = max(favorite_genres, key=favorite_genres.get)
        
        # Рекомендуем книги из этого жанра, которых нет в избранном
        recommendations = [
            book for book in self.books 
            if book.genre == top_genre and not book.favorite
        ]
        
        return recommendations[:5]
    
    def save_to_file(self):
        """Сохраняет данные в файл"""
        try:
            data = [book.to_dict() for book in self.books]
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"\n❌ Ошибка при сохранении в файл: {e}")
    
    def load_from_file(self):
        """Загружает данные из файла"""
        if not os.path.exists(self.filename):
            return
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.books = [Book.from_dict(book_data) for book_data in data]
            print(f"\n📚 Загружено {len(self.books)} книг из файла.")
        except Exception as e:
            print(f"\n❌ Ошибка при загрузке из файла: {e}")
            self.books = []


def display_books(books, title="Книги в библиотеке"):
    """Отображает список книг в удобном формате"""
    if not books:
        print("\n📭 Список пуст.")
        return
    
    print(f"\n{'='*60}")
    print(f"{title:^60}")
    print(f"{'='*60}")
    
    for i, book in enumerate(books, 1):
        print(f"\n{i}. {book}")
        print(f"   📝 {book.description[:100]}..." if len(book.description) > 100 else f"   📝 {book.description}")
        print(f"   🆔 ID: {book.id}")


def main():
    """Основная функция приложения"""
    library = Library()
    
    while True:
        print("\n" + "="*50)
        print("           📚 T-БИБЛИОТЕКА 📚")
        print("="*50)
        print("\nГЛАВНОЕ МЕНЮ:")
        print("1. 📖 Добавить книгу")
        print("2. 📋 Просмотреть все книги")
        print("3. 🔍 Поиск книги")
        print("4. ⭐ Избранное")
        print("5. 🔄 Изменить статус книги")
        print("6. 🎯 Рекомендации для вас")
        print("7. 🗑️ Удалить книгу")
        print("8. 💾 Сохранить данные")
        print("9. ❌ Выход")
        
        choice = input("\nВыберите действие (1-9): ").strip()
        
        if choice == '1':
            # Добавление книги
            print("\n📖 ДОБАВЛЕНИЕ НОВОЙ КНИГИ")
            title = input("Название: ").strip()
            if not title:
                print("❌ Название не может быть пустым!")
                continue
            
            author = input("Автор: ").strip()
            if not author:
                print("❌ Автор не может быть пустым!")
                continue
            
            genre = input("Жанр: ").strip()
            year = input("Год издания: ").strip()
            description = input("Краткое описание: ").strip()
            
            library.add_book(title, author, genre, year, description)
        
        elif choice == '2':
            # Просмотр всех книг с сортировкой и фильтрацией
            if not library.books:
                print("\n📭 Библиотека пуста. Добавьте первую книгу!")
                continue
            
            print("\n📋 ПРОСМОТР КНИГ")
            print("1. Показать все книги")
            print("2. Сортировать")
            print("3. Фильтровать")
            
            sub_choice = input("Выберите действие: ").strip()
            
            if sub_choice == '1':
                display_books(library.get_all_books())
            
            elif sub_choice == '2':
                print("\nСортировать по:")
                print("1. Названию")
                print("2. Автору")
                print("3. Году")
                print("4. Жанру")
                
                sort_choice = input("Выберите: ").strip()
                sort_map = {'1': 'название', '2': 'автор', '3': 'год', '4': 'жанр'}
                
                if sort_choice in sort_map:
                    order = input("Порядок (1 - по возрастанию, 2 - по убыванию): ").strip()
                    reverse = (order == '2')
                    sorted_books = library.sort_books(sort_map[sort_choice], reverse)
                    display_books(sorted_books, f"Книги (сортировка по {sort_map[sort_choice]})")
                else:
                    print("❌ Неверный выбор!")
            
            elif sub_choice == '3':
                print("\nФильтровать по:")
                print("1. Жанру")
                print("2. Статусу")
                
                filter_choice = input("Выберите: ").strip()
                
                if filter_choice == '1':
                    genre = input("Введите жанр: ").strip()
                    filtered = library.filter_books('жанр', genre)
                    display_books(filtered, f"Книги в жанре '{genre}'")
                elif filter_choice == '2':
                    print("Статус: 1 - прочитана, 2 - не прочитана")
                    status_choice = input("Выберите: ").strip()
                    status = 'прочитана' if status_choice == '1' else 'не прочитана'
                    filtered = library.filter_books('статус', status)
                    display_books(filtered, f"Книги со статусом '{status}'")
                else:
                    print("❌ Неверный выбор!")
        
        elif choice == '3':
            # Поиск книг
            keyword = input("\nВведите ключевое слово для поиска: ").strip()
            if keyword:
                results = library.search_books(keyword)
                display_books(results, f"Результаты поиска: '{keyword}'")
            else:
                print("❌ Введите ключевое слово!")
        
        elif choice == '4':
            # Избранное
            favorites = library.get_favorites()
            display_books(favorites, "⭐ ИЗБРАННЫЕ КНИГИ")
            
            if favorites:
                print("\n1. Добавить/удалить из избранного")
                print("2. Вернуться в меню")
                
                fav_choice = input("Выберите: ").strip()
                if fav_choice == '1':
                    try:
                        book_id = float(input("Введите ID книги: ").strip())
                        library.toggle_favorite(book_id)
                    except ValueError:
                        print("❌ Некорректный ID!")
        
        elif choice == '5':
            # Изменение статуса
            if not library.books:
                print("\n📭 Библиотека пуста!")
                continue
            
            try:
                book_id = float(input("\nВведите ID книги: ").strip())
                book = library.find_book_by_id(book_id)
                
                if book:
                    print(f"\nТекущий статус книги '{book.title}': {book.status}")
                    print("1. Прочитана")
                    print("2. Не прочитана")
                    
                    status_choice = input("Выберите новый статус: ").strip()
                    new_status = 'прочитана' if status_choice == '1' else 'не прочитана'
                    library.change_status(book_id, new_status)
                else:
                    print("❌ Книга не найдена!")
            except ValueError:
                print("❌ Некорректный ID!")
        
        elif choice == '6':
            # Рекомендации
            recommendations = library.get_recommendations()
            if recommendations:
                display_books(recommendations, "🎯 РЕКОМЕНДАЦИИ ДЛЯ ВАС")
            else:
                print("\n📭 Нет рекомендаций. Добавьте книги в избранное!")
        
        elif choice == '7':
            # Удаление книги
            if not library.books:
                print("\n📭 Библиотека пуста!")
                continue
            
            display_books(library.get_all_books())
            
            try:
                book_id = float(input("\nВведите ID книги для удаления: ").strip())
                confirm = input("Вы уверены? (да/нет): ").strip().lower()
                if confirm == 'да':
                    library.delete_book(book_id)
            except ValueError:
                print("❌ Некорректный ID!")
        
        elif choice == '8':
            # Сохранение данных
            library.save_to_file()
            print("\n💾 Данные успешно сохранены в файл!")
        
        elif choice == '9':
            # Выход
            print("\n💾 Сохраняем данные перед выходом...")
            library.save_to_file()
            print("👋 До свидания! Спасибо за использование T-Библиотеки!")
            break
        
        else:
            print("\n❌ Неверный выбор! Пожалуйста, выберите 1-9.")


if __name__ == "__main__":
    main()