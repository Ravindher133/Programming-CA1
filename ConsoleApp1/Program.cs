using System;
using System.Collections.Generic;

namespace ContactBookApp
{
    public class Contact
    {
        public string FirstName { get; set; }
        public string LastName { get; set; }
        public string Company { get; set; }
        private string mobileNumber;

        public string MobileNumber
        {
            get { return mobileNumber; }
            set
            {
                if (IsValidMobile(value))
                    mobileNumber = value;
                else
                    throw new Exception("Invalid Mobile Number! Must be a non-zero 9-digit number.");
            }
        }

        public string Email { get; set; }
        public DateTime Birthdate { get; set; }

        public void SetName(string firstName)
        {
            FirstName = firstName;
        }

        public void SetName(string firstName, string lastName)
        {
            FirstName = firstName;
            LastName = lastName;
        }

        private bool IsValidMobile(string number)
        {
            return number.Length == 9 && long.TryParse(number, out long n) && n > 0;
        }

        public override string ToString()
        {
            return $"{FirstName} {LastName} - {MobileNumber}";
        }
    }
    public class ContactBook
    {
        private List<Contact> contacts = new List<Contact>();

        public void AddContact(Contact c)
        {
            if (contacts.Count >= 20)
                Console.WriteLine("Contact list already has minimum 20 contacts.");

            contacts.Add(c);
            Console.WriteLine("Contact added successfully!\n");
        }

        public void ShowAllContacts()
        {
            if (contacts.Count == 0)
            {
                Console.WriteLine("No contacts available.\n");
                return;
            }

            Console.WriteLine("\n--- Contact List ---");
            for (int i = 0; i < contacts.Count; i++)
            {
                Console.WriteLine($"{i + 1}. {contacts[i]}");
            }
            Console.WriteLine();
        }
        public void ShowContactDetails(int index)
        {
            if (index < 0 || index >= contacts.Count)
            {
                Console.WriteLine("Invalid contact index.\n");
                return;
            }

            Contact c = contacts[index];
            Console.WriteLine("\n--- Contact Details ---");
            Console.WriteLine($"Name: {c.FirstName} {c.LastName}");
            Console.WriteLine($"Company: {c.Company}");
            Console.WriteLine($"Mobile: {c.MobileNumber}");
            Console.WriteLine($"Email: {c.Email}");
            Console.WriteLine($"Birthdate: {c.Birthdate.ToShortDateString()}\n");
        }
        public void UpdateContact(int index)
        {
            if (index < 0 || index >= contacts.Count)
            {
                Console.WriteLine("Invalid contact index.\n");
                return;
            }

            Contact c = contacts[index];

            Console.Write("Enter New First Name: ");
            c.FirstName = Console.ReadLine();

            Console.Write("Enter New Last Name: ");
            c.LastName = Console.ReadLine();

            Console.Write("Enter New Company: ");
            c.Company = Console.ReadLine();

            Console.Write("Enter New Mobile Number (9 digits): ");
            try
            {
                c.MobileNumber = Console.ReadLine();
            }
            catch (Exception ex)
            {
                Console.WriteLine(ex.Message);
            }

            Console.Write("Enter New Email: ");
            c.Email = Console.ReadLine();

            Console.Write("Enter New Birthdate (yyyy-mm-dd): ");
            c.Birthdate = DateTime.Parse(Console.ReadLine());

            Console.WriteLine("Contact updated successfully!\n");
        }
        public void DeleteContact(int index)
        {
            if (index < 0 || index >= contacts.Count)
            {
                Console.WriteLine("Invalid contact index.\n");
                return;
            }

            contacts.RemoveAt(index);
            Console.WriteLine("Contact deleted successfully!\n");
        }
    }
    class Program
    {
        static void Main(string[] args)
        {
            ContactBook book = new ContactBook();
            int choice;

            do
            {
                Console.WriteLine("---- CONTACT BOOK MENU ----");
                Console.WriteLine("1: Add Contact");
                Console.WriteLine("2: Show All Contacts");
                Console.WriteLine("3: Show Contact Details");
                Console.WriteLine("4: Update Contact");
                Console.WriteLine("5: Delete Contact");
                Console.WriteLine("0: Exit");
                Console.Write("Enter choice: ");

                int.TryParse(Console.ReadLine(), out choice);
                Console.WriteLine();

                switch (choice)
                {
                    case 1:
                        Contact c = new Contact();

                        Console.Write("Enter First Name: ");
                        c.FirstName = Console.ReadLine();

                        Console.Write("Enter Last Name: ");
                        c.LastName = Console.ReadLine();

                        Console.Write("Enter Company: ");
                        c.Company = Console.ReadLine();

                        Console.Write("Enter Mobile Number (9-digit): ");
                        try
                        {
                            c.MobileNumber = Console.ReadLine();
                        }
                        catch (Exception ex)
                        {
                            Console.WriteLine(ex.Message + "\n");
                            break;
                        }

                        Console.Write("Enter Email: ");
                        c.Email = Console.ReadLine();

                        Console.Write("Enter Birthdate (yyyy-mm-dd): ");
                        c.Birthdate = DateTime.Parse(Console.ReadLine());

                        book.AddContact(c);
                        break;

                    case 2:
                        book.ShowAllContacts();
                        break;

                    case 3:
                        Console.Write("Enter Contact Number to View: ");
                        int d = int.Parse(Console.ReadLine()) - 1;
                        book.ShowContactDetails(d);
                        break;

                    case 4:
                        Console.Write("Enter Contact Number to Update: ");
                        int u = int.Parse(Console.ReadLine()) - 1;
                        book.UpdateContact(u);
                        break;

                    case 5:
                        Console.Write("Enter Contact Number to Delete: ");
                        int del = int.Parse(Console.ReadLine()) - 1;
                        book.DeleteContact(del);
                        break;

                    case 0:
                        Console.WriteLine("Exiting...");
                        break;

                    default:
                        Console.WriteLine("Invalid choice. Try again.\n");
                        break;
                }

            } while (choice != 0);
        }
    }
}
