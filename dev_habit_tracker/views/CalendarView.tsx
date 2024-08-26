import React from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';

interface CalendarViewProps {
  selectedDate: Date;
  onSelectDate: (date: Date) => void;
}

const CalendarView: React.FC<CalendarViewProps> = ({ selectedDate, onSelectDate }) => {
  const generateDates = (startDate: Date, numDays: number) => {
    const dates = [];
    for (let i = 0; i < numDays; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() - i);
      dates.push(date);
    }
    return dates.reverse();
  };

  const dates = generateDates(new Date(), 7);

  const isToday = (date: Date) => {
    const today = new Date();
    return date.getDate() === today.getDate() &&
           date.getMonth() === today.getMonth() &&
           date.getFullYear() === today.getFullYear();
  };

  const isSelected = (date: Date) => {
    return date.getDate() === selectedDate.getDate() &&
           date.getMonth() === selectedDate.getMonth() &&
           date.getFullYear() === selectedDate.getFullYear();
  };

  return (
    <View style={styles.container}>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.scrollView}>
        {dates.map((date, index) => (
          <TouchableOpacity
            key={index}
            style={[
              styles.dateContainer,
              isSelected(date) && styles.selectedDate,
              isToday(date) && styles.today
            ]}
            onPress={() => onSelectDate(date)}
          >
            <Text style={[styles.dayText, isSelected(date) && styles.selectedText]}>
              {date.toLocaleString('default', { weekday: 'short' })}
            </Text>
            <Text style={[styles.dateText, isSelected(date) && styles.selectedText]}>
              {date.getDate()}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#f0f8ff',
    paddingVertical: 20,
  },
  scrollView: {
    paddingHorizontal: 10,
  },
  dateContainer: {
    width: 60,
    height: 80,
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 5,
    borderRadius: 15,
    backgroundColor: '#ffffff',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 2,
    elevation: 3,
  },
  selectedDate: {
    backgroundColor: '#4a90e2',
  },
  today: {
    borderColor: '#4a90e2',
    borderWidth: 2,
  },
  dayText: {
    fontSize: 14,
    color: '#666',
    marginBottom: 5,
  },
  dateText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  selectedText: {
    color: '#ffffff',
  },
});

export default CalendarView;