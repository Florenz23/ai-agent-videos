import React from 'react';
import { View, Text, StyleSheet, FlatList, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface Habit {
  id: string;
  name: string;
  description: string;
}

interface HabitViewProps {
  habits: Habit[];
  habitLogs: Record<string, Record<string, boolean>>;
  selectedDate: Date;
  onToggleHabit: (habitId: string) => void;
  onEditHabit: (habit: Habit) => void;
}

const HabitView: React.FC<HabitViewProps> = ({ 
  habits, 
  habitLogs, 
  selectedDate, 
  onToggleHabit, 
  onEditHabit 
}) => {
  const formatDate = (date: Date) => {
    return date.toISOString().split('T')[0];
  };

  const renderHabitItem = ({ item }: { item: Habit }) => {
    const isCompleted = habitLogs[formatDate(selectedDate)]?.[item.id] || false;

    return (
      <View style={styles.habitItem}>
        <TouchableOpacity 
          style={[styles.checkbox, isCompleted && styles.checkboxCompleted]} 
          onPress={() => onToggleHabit(item.id)}
        >
          {isCompleted && <Ionicons name="checkmark" size={24} color="#ffffff" />}
        </TouchableOpacity>
        <View style={styles.habitInfo}>
          <Text style={styles.habitName}>{item.name}</Text>
          <Text style={styles.habitDescription}>{item.description}</Text>
        </View>
        <TouchableOpacity 
          style={styles.editButton} 
          onPress={() => onEditHabit(item)}
        >
          <Ionicons name="pencil" size={20} color="#4a90e2" />
        </TouchableOpacity>
      </View>
    );
  };

  return (
    <FlatList
      data={habits}
      renderItem={renderHabitItem}
      keyExtractor={(item) => item.id}
      style={styles.container}
    />
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  habitItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  checkbox: {
    width: 28,
    height: 28,
    borderWidth: 2,
    borderColor: '#4a90e2',
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 15,
  },
  checkboxCompleted: {
    backgroundColor: '#4a90e2',
  },
  habitInfo: {
    flex: 1,
  },
  habitName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  habitDescription: {
    fontSize: 14,
    color: '#666',
  },
  editButton: {
    padding: 5,
  },
});

export default HabitView;